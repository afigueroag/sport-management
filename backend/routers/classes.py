"""
Classes Router - Gestión de clases CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from database import get_db
from models.class_model import Class
from models.user import User
from schemas.class_schema import ClassCreate, ClassResponse, ClassUpdate
from routers.auth import get_current_user

router = APIRouter(tags=["Classes"])


@router.get("", response_model=list[ClassResponse])
async def list_classes(
    sport_type: str = Query(None),
    day_of_week: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista todas las clases activas

    - **sport_type**: Filtrar por tipo de deporte (opcional)
    - **day_of_week**: Filtrar por día de la semana (opcional)
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Límite de registros a devolver
    """
    query = select(Class).where(Class.is_active == True).offset(skip).limit(limit)

    if sport_type:
        query = query.where(Class.sport_type.ilike(f"%{sport_type}%"))

    if day_of_week:
        query = query.where(Class.day_of_week == day_of_week)

    result = await db.execute(query)
    classes = result.scalars().all()

    return classes


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(
    class_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene una clase por ID
    """
    result = await db.execute(
        select(Class).where(Class.id == class_id)
    )
    class_obj = result.scalars().first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    return class_obj


@router.post("", response_model=ClassResponse)
async def create_class(
    class_data: ClassCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea una nueva clase

    Solo admin e instructores pueden crear clases
    """
    if current_user.role.value not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear clases",
        )

    # Si es instructor, la clase es para él. Si es admin, requiere instructor_id
    # Por ahora, el instructor crea clases para sí mismo
    instructor_id = current_user.id if current_user.role.value == "instructor" else current_user.id

    class_obj = Class(
        id=str(uuid.uuid4()),
        name=class_data.name,
        sport_type=class_data.sport_type,
        instructor_id=instructor_id,
        capacity=class_data.capacity,
        day_of_week=class_data.day_of_week,
        start_time=class_data.start_time,
        end_time=class_data.end_time,
    )
    db.add(class_obj)

    try:
        await db.commit()
        await db.refresh(class_obj)
        return class_obj
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear clase",
        )


@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: str,
    class_data: ClassUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza una clase

    El instructor puede actualizar sus propias clases, solo admin puede actualizar otras
    """
    # Obtener clase
    result = await db.execute(
        select(Class).where(Class.id == class_id)
    )
    class_obj = result.scalars().first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    # Verificar permisos
    if (
        current_user.id != class_obj.instructor_id
        and current_user.role.value != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar esta clase",
        )

    # Actualizar campos
    update_data = class_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(class_obj, field, value)

    try:
        await db.commit()
        await db.refresh(class_obj)
        return class_obj
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar clase",
        )


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Elimina una clase (soft delete)

    Solo admin puede eliminar clases
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar clases",
        )

    # Obtener clase
    result = await db.execute(
        select(Class).where(Class.id == class_id)
    )
    class_obj = result.scalars().first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    # Soft delete: marcar como inactiva
    class_obj.is_active = False
    await db.commit()

    return None
