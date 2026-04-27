"""
Students Router - Gestión de estudiantes CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from database import get_db
from models.student import Student
from models.user import User
from schemas.student import StudentCreate, StudentResponse, StudentUpdate
from routers.auth import get_current_user

router = APIRouter(tags=["Students"])


@router.get("", response_model=list[StudentResponse])
async def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista todos los estudiantes

    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Límite de registros a devolver
    """
    # Solo admin puede listar todos
    if current_user.role.value not in ["admin", "receptionist"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para listar estudiantes",
        )

    result = await db.execute(
        select(Student).offset(skip).limit(limit)
    )
    students = result.scalars().all()

    return students


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene un estudiante por ID
    """
    # Usuario puede ver su propio perfil, admin puede ver cualquiera
    if (
        current_user.id != student_id
        and current_user.role.value != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este estudiante",
        )

    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    return student


@router.post("", response_model=StudentResponse)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea un nuevo estudiante

    Solo admin y recepcionistas pueden crear estudiantes
    """
    if current_user.role.value not in ["admin", "receptionist"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear estudiantes",
        )

    # Verificar si el email ya existe
    result = await db.execute(
        select(User).where(User.email == student_data.email.lower())
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este email ya está registrado",
        )

    # Crear usuario
    from utils.security import hash_password
    from models.user import UserRole

    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=student_data.email.lower(),
        full_name=student_data.full_name,
        password_hash=hash_password(student_data.password),
        role=UserRole.STUDENT,
    )
    db.add(user)
    await db.flush()

    # Crear registro de estudiante
    student = Student(
        id=user_id,
        phone=student_data.phone,
        date_of_birth=student_data.date_of_birth,
        emergency_contact_name=student_data.emergency_contact_name,
        emergency_contact_phone=student_data.emergency_contact_phone,
    )
    db.add(student)

    try:
        await db.commit()
        await db.refresh(student)
        return student
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear estudiante",
        )


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza un estudiante

    El usuario puede actualizar su propio perfil, solo admin puede actualizar otros
    """
    if (
        current_user.id != student_id
        and current_user.role.value != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este estudiante",
        )

    # Obtener estudiante
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    # Actualizar campos
    update_data = student_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)

    try:
        await db.commit()
        await db.refresh(student)
        return student
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar estudiante",
        )


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Elimina un estudiante (soft delete)

    Solo admin puede eliminar estudiantes
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar estudiantes",
        )

    # Obtener estudiante
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    # Soft delete: marcar usuario como inactivo
    result = await db.execute(
        select(User).where(User.id == student_id)
    )
    user = result.scalars().first()

    if user:
        user.is_active = False
        await db.commit()

    return None
