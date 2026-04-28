"""
Class Sessions Router - Gestión de sesiones de clases
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import uuid

from ..database import get_db
from ..models.class_model import Class, ClassSession
from ..models.user import User
from ..schemas.class_session_schema import ClassSessionCreate, ClassSessionResponse, ClassSessionUpdate
from .auth import get_current_user

router = APIRouter(tags=["Class Sessions"])


@router.get("", response_model=list[ClassSessionResponse])
async def list_class_sessions(
    class_id: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista sesiones de clase

    - **class_id**: Filtrar por clase (requerido)
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Límite de registros a devolver
    """
    if not class_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere filtrar por class_id",
        )

    # Verificar que la clase existe
    result = await db.execute(
        select(Class).where(Class.id == class_id)
    )
    class_obj = result.scalars().first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    # Obtener sesiones
    result = await db.execute(
        select(ClassSession)
        .where(ClassSession.class_id == class_id)
        .offset(skip)
        .limit(limit)
    )
    sessions = result.scalars().all()

    return sessions


@router.get("/{session_id}", response_model=ClassSessionResponse)
async def get_class_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene una sesión de clase por ID
    """
    result = await db.execute(
        select(ClassSession).where(ClassSession.id == session_id)
    )
    session = result.scalars().first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión de clase no encontrada",
        )

    return session


@router.post("", response_model=ClassSessionResponse)
async def create_class_session(
    session_data: ClassSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea una nueva sesión de clase

    Solo instructores pueden crear sesiones de sus propias clases, admin puede crear cualquiera
    """
    if current_user.role.value not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear sesiones",
        )

    # Verificar que la clase existe
    result = await db.execute(
        select(Class).where(Class.id == session_data.class_id)
    )
    class_obj = result.scalars().first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    # Si es instructor, verificar que es su clase
    if current_user.role.value == "instructor":
        if class_obj.instructor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para crear sesiones en esta clase",
            )

    # Verificar que la fecha de sesión es en el futuro
    if session_data.session_date < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de sesión debe ser en el futuro",
        )

    session = ClassSession(
        id=str(uuid.uuid4()),
        class_id=session_data.class_id,
        session_date=session_data.session_date,
    )
    db.add(session)

    try:
        await db.commit()
        await db.refresh(session)
        return session
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear sesión de clase",
        )


@router.put("/{session_id}", response_model=ClassSessionResponse)
async def update_class_session(
    session_id: str,
    session_data: ClassSessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza una sesión de clase

    El instructor puede actualizar sus propias sesiones, admin puede actualizar cualquiera
    """
    # Obtener sesión
    result = await db.execute(
        select(ClassSession).where(ClassSession.id == session_id)
    )
    session = result.scalars().first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión de clase no encontrada",
        )

    # Obtener la clase para verificar permisos
    result = await db.execute(
        select(Class).where(Class.id == session.class_id)
    )
    class_obj = result.scalars().first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    # Verificar permisos
    if (
        current_user.role.value == "instructor"
        and class_obj.instructor_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar esta sesión",
        )

    if current_user.role.value not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar sesiones",
        )

    # Actualizar campos
    update_data = session_data.dict(exclude_unset=True)

    # Validar fecha si se intenta actualizar
    if "session_date" in update_data and update_data["session_date"]:
        if update_data["session_date"] < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de sesión debe ser en el futuro",
            )

    for field, value in update_data.items():
        setattr(session, field, value)

    try:
        await db.commit()
        await db.refresh(session)
        return session
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar sesión",
        )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Elimina una sesión de clase

    Solo admin puede eliminar sesiones
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar sesiones",
        )

    # Obtener sesión
    result = await db.execute(
        select(ClassSession).where(ClassSession.id == session_id)
    )
    session = result.scalars().first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión de clase no encontrada",
        )

    await db.delete(session)
    await db.commit()

    return None
