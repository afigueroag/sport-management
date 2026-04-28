"""
Enrollments Router - Gestión de inscripciones de estudiantes en clases
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from datetime import datetime
import uuid

from ..database import get_db
from ..models.enrollment import Enrollment, EnrollmentStatus
from ..models.class_model import Class
from ..models.student import Student
from ..models.user import User
from ..schemas.enrollment_schema import EnrollmentCreate, EnrollmentResponse, EnrollmentUpdate
from .auth import get_current_user

router = APIRouter(tags=["Enrollments"])


@router.get("", response_model=list[EnrollmentResponse])
async def list_enrollments(
    student_id: str = Query(None),
    class_id: str = Query(None),
    status_filter: EnrollmentStatus = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista todas las inscripciones

    - **student_id**: Filtrar por estudiante (opcional)
    - **class_id**: Filtrar por clase (opcional)
    - **status_filter**: Filtrar por estado (active/paused/canceled) (opcional)
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Límite de registros a devolver
    """
    query = select(Enrollment).offset(skip).limit(limit)

    # Estudiantes solo ven sus propias inscripciones
    if current_user.role.value == "student":
        query = query.where(Enrollment.student_id == current_user.id)
    elif student_id:
        # Otros roles pueden filtrar por student_id
        query = query.where(Enrollment.student_id == student_id)

    if class_id:
        query = query.where(Enrollment.class_id == class_id)

    if status_filter:
        query = query.where(Enrollment.status == status_filter)

    result = await db.execute(query)
    enrollments = result.scalars().all()

    return enrollments


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment(
    enrollment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene una inscripción por ID
    """
    result = await db.execute(
        select(Enrollment).where(Enrollment.id == enrollment_id)
    )
    enrollment = result.scalars().first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscripción no encontrada",
        )

    # Estudiantes solo ven sus propias inscripciones
    if (
        current_user.role.value == "student"
        and current_user.id != enrollment.student_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta inscripción",
        )

    return enrollment


@router.post("", response_model=EnrollmentResponse)
async def create_enrollment(
    enrollment_data: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea una nueva inscripción (enroll a student in a class)

    Estudiantes pueden inscribirse a sí mismos, admin puede inscribir a cualquiera
    """
    # Verificar permisos
    if (
        current_user.role.value == "student"
        and current_user.id != enrollment_data.student_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para inscribir a otros estudiantes",
        )

    if current_user.role.value not in ["student", "admin", "receptionist"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear inscripciones",
        )

    # Verificar que el estudiante existe
    result = await db.execute(
        select(Student).where(Student.id == enrollment_data.student_id)
    )
    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    # Verificar que la clase existe
    result = await db.execute(
        select(Class).where(Class.id == enrollment_data.class_id)
    )
    class_obj = result.scalars().first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    # Verificar que la clase está activa
    if not class_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La clase no está activa",
        )

    # Verificar que no existe una inscripción activa
    result = await db.execute(
        select(Enrollment).where(
            and_(
                Enrollment.student_id == enrollment_data.student_id,
                Enrollment.class_id == enrollment_data.class_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
        )
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El estudiante ya está inscrito en esta clase",
        )

    enrollment = Enrollment(
        id=str(uuid.uuid4()),
        student_id=enrollment_data.student_id,
        class_id=enrollment_data.class_id,
    )
    db.add(enrollment)

    try:
        await db.commit()
        await db.refresh(enrollment)
        return enrollment
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear inscripción",
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear inscripción",
        )


@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
async def update_enrollment(
    enrollment_id: str,
    enrollment_data: EnrollmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza una inscripción (cambiar estado)

    Estudiantes pueden actualizar sus propias inscripciones, admin puede actualizar cualquiera
    """
    # Obtener inscripción
    result = await db.execute(
        select(Enrollment).where(Enrollment.id == enrollment_id)
    )
    enrollment = result.scalars().first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscripción no encontrada",
        )

    # Verificar permisos
    if (
        current_user.role.value == "student"
        and current_user.id != enrollment.student_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar esta inscripción",
        )

    if current_user.role.value not in ["student", "admin", "receptionist"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar inscripciones",
        )

    # Actualizar campo de estado
    update_data = enrollment_data.dict(exclude_unset=True)
    if "status" in update_data:
        enrollment.status = update_data["status"]
        if update_data["status"] == EnrollmentStatus.CANCELED:
            enrollment.canceled_at = datetime.utcnow()

    try:
        await db.commit()
        await db.refresh(enrollment)
        return enrollment
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar inscripción",
        )


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Elimina una inscripción (cancela la inscripción)

    Estudiantes pueden cancelar sus propias inscripciones, admin puede cancelar cualquiera
    """
    # Obtener inscripción
    result = await db.execute(
        select(Enrollment).where(Enrollment.id == enrollment_id)
    )
    enrollment = result.scalars().first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscripción no encontrada",
        )

    # Verificar permisos
    if (
        current_user.role.value == "student"
        and current_user.id != enrollment.student_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para cancelar esta inscripción",
        )

    if current_user.role.value not in ["student", "admin", "receptionist"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cancelar inscripciones",
        )

    # Soft delete: cambiar estado a CANCELED
    enrollment.status = EnrollmentStatus.CANCELED
    enrollment.canceled_at = datetime.utcnow()
    await db.commit()

    return None
