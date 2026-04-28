"""
Attendance Router - Gestión de asistencia en clases
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from datetime import datetime
import uuid

from ..database import get_db
from ..models.attendance import Attendance, AttendanceStatus
from ..models.class_model import ClassSession, Class
from ..models.student import Student
from ..models.user import User
from ..schemas.attendance_schema import AttendanceCreate, AttendanceResponse, AttendanceUpdate
from .auth import get_current_user

router = APIRouter(tags=["Attendance"])


@router.get("", response_model=list[AttendanceResponse])
async def list_attendance(
    student_id: str = Query(None),
    class_session_id: str = Query(None),
    status_filter: AttendanceStatus = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista registros de asistencia

    - **student_id**: Filtrar por estudiante (opcional)
    - **class_session_id**: Filtrar por sesión de clase (opcional)
    - **status_filter**: Filtrar por estado (present/absent/excused) (opcional)
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Límite de registros a devolver
    """
    query = select(Attendance).offset(skip).limit(limit)

    # Estudiantes solo ven su propia asistencia
    if current_user.role.value == "student":
        query = query.where(Attendance.student_id == current_user.id)
    elif student_id:
        # Otros roles pueden filtrar por student_id
        query = query.where(Attendance.student_id == student_id)

    if class_session_id:
        query = query.where(Attendance.class_session_id == class_session_id)

    if status_filter:
        query = query.where(Attendance.status == status_filter)

    result = await db.execute(query)
    attendance_records = result.scalars().all()

    return attendance_records


@router.get("/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance(
    attendance_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene un registro de asistencia por ID
    """
    result = await db.execute(
        select(Attendance).where(Attendance.id == attendance_id)
    )
    attendance = result.scalars().first()

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de asistencia no encontrado",
        )

    # Estudiantes solo ven su propia asistencia
    if (
        current_user.role.value == "student"
        and current_user.id != attendance.student_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este registro",
        )

    return attendance


@router.post("", response_model=AttendanceResponse)
async def mark_attendance(
    attendance_data: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Marca asistencia de un estudiante en una sesión de clase

    Solo instructores y admin pueden marcar asistencia
    """
    if current_user.role.value not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para marcar asistencia",
        )

    # Verificar que el estudiante existe
    result = await db.execute(
        select(Student).where(Student.id == attendance_data.student_id)
    )
    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    # Verificar que la sesión de clase existe
    result = await db.execute(
        select(ClassSession).where(
            ClassSession.id == attendance_data.class_session_id
        )
    )
    class_session = result.scalars().first()

    if not class_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión de clase no encontrada",
        )

    # Si es instructor, verificar que la sesión es de su clase
    if current_user.role.value == "instructor":
        result = await db.execute(
            select(Class).where(Class.id == class_session.class_id)
        )
        class_obj = result.scalars().first()

        if not class_obj or class_obj.instructor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para marcar asistencia en esta clase",
            )

    # Verificar que no existe ya un registro de asistencia para este estudiante y sesión
    result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.student_id == attendance_data.student_id,
                Attendance.class_session_id == attendance_data.class_session_id,
            )
        )
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un registro de asistencia para este estudiante en esta sesión",
        )

    attendance = Attendance(
        id=str(uuid.uuid4()),
        student_id=attendance_data.student_id,
        class_session_id=attendance_data.class_session_id,
        marked_by=current_user.id,
        status=attendance_data.status,
        notes=attendance_data.notes,
    )
    db.add(attendance)

    try:
        await db.commit()
        await db.refresh(attendance)
        return attendance
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al marcar asistencia",
        )


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: str,
    attendance_data: AttendanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza un registro de asistencia

    Solo el instructor que marcó o admin pueden actualizar
    """
    # Obtener registro
    result = await db.execute(
        select(Attendance).where(Attendance.id == attendance_id)
    )
    attendance = result.scalars().first()

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de asistencia no encontrado",
        )

    # Verificar permisos
    if (
        current_user.id != attendance.marked_by
        and current_user.role.value != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este registro",
        )

    # Actualizar campos
    update_data = attendance_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)

    attendance.marked_at = datetime.utcnow()

    try:
        await db.commit()
        await db.refresh(attendance)
        return attendance
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar asistencia",
        )


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance(
    attendance_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Elimina un registro de asistencia

    Solo admin puede eliminar registros
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar registros de asistencia",
        )

    # Obtener registro
    result = await db.execute(
        select(Attendance).where(Attendance.id == attendance_id)
    )
    attendance = result.scalars().first()

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de asistencia no encontrado",
        )

    await db.delete(attendance)
    await db.commit()

    return None
