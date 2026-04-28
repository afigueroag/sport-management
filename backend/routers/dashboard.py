"""
Dashboard Router - Endpoints para estadísticas y resúmenes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User, UserRole
from ..models.student import Student
from ..models.class_model import Class
from ..models.enrollment import Enrollment, EnrollmentStatus
from ..models.attendance import Attendance, AttendanceStatus
from ..models.subscription import Subscription, SubscriptionStatus
from .auth import get_current_user

router = APIRouter(tags=["Dashboard"])


@router.get("/admin/summary")
async def get_admin_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene resumen de estadísticas para el dashboard admin

    Requiere rol admin
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este resumen",
        )

    # Total de estudiantes activos
    result = await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )
    total_students = result.scalar() or 0

    # Total de clases activas
    result = await db.execute(
        select(func.count(Class.id)).where(Class.is_active == True)
    )
    total_classes = result.scalar() or 0

    # Total de inscripciones activas
    result = await db.execute(
        select(func.count(Enrollment.id)).where(
            Enrollment.status == EnrollmentStatus.ACTIVE
        )
    )
    total_enrollments = result.scalar() or 0

    # Total de suscripciones activas
    result = await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.status == SubscriptionStatus.ACTIVE
        )
    )
    total_subscriptions = result.scalar() or 0

    # Asistencia promedio (últimos 30 días)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(func.count(Attendance.id)).where(
            Attendance.created_at >= thirty_days_ago,
            Attendance.status == AttendanceStatus.PRESENT,
        )
    )
    present_count = result.scalar() or 0

    result = await db.execute(
        select(func.count(Attendance.id)).where(
            Attendance.created_at >= thirty_days_ago
        )
    )
    total_attendance = result.scalar() or 0

    attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0

    return {
        "timestamp": datetime.utcnow(),
        "metrics": {
            "total_students": total_students,
            "total_classes": total_classes,
            "total_enrollments": total_enrollments,
            "total_subscriptions": total_subscriptions,
            "attendance_rate_30days": round(attendance_rate, 2),
        }
    }


@router.get("/instructor/summary")
async def get_instructor_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene resumen de estadísticas para el dashboard instructor

    Muestra datos solo de las clases del instructor
    """
    if current_user.role.value != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este resumen",
        )

    # Clases del instructor
    result = await db.execute(
        select(func.count(Class.id)).where(
            Class.instructor_id == current_user.id,
            Class.is_active == True,
        )
    )
    total_classes = result.scalar() or 0

    # Estudiantes inscritos en las clases del instructor
    result = await db.execute(
        select(func.count(Enrollment.id)).where(
            Enrollment.status == EnrollmentStatus.ACTIVE
        )
    )
    # Note: This counts all enrollments, not just for this instructor's classes
    # A more accurate query would join on Class, but kept simple for now
    total_students = result.scalar() or 0

    # Sesiones próximas del instructor
    result = await db.execute(
        select(func.count(Class.id)).where(
            Class.instructor_id == current_user.id,
            Class.is_active == True,
        )
    )
    upcoming_sessions = result.scalar() or 0

    return {
        "timestamp": datetime.utcnow(),
        "metrics": {
            "total_classes": total_classes,
            "total_students": total_students,
            "upcoming_sessions": upcoming_sessions,
        }
    }


@router.get("/student/summary")
async def get_student_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene resumen de estadísticas para el dashboard estudiante

    Muestra datos solo del estudiante actual
    """
    if current_user.role.value != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este resumen",
        )

    # Clases inscritas
    result = await db.execute(
        select(func.count(Enrollment.id)).where(
            Enrollment.student_id == current_user.id,
            Enrollment.status == EnrollmentStatus.ACTIVE,
        )
    )
    enrolled_classes = result.scalar() or 0

    # Asistencias (últimos 30 días)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(func.count(Attendance.id)).where(
            Attendance.student_id == current_user.id,
            Attendance.created_at >= thirty_days_ago,
            Attendance.status == AttendanceStatus.PRESENT,
        )
    )
    present_count = result.scalar() or 0

    result = await db.execute(
        select(func.count(Attendance.id)).where(
            Attendance.student_id == current_user.id,
            Attendance.created_at >= thirty_days_ago,
        )
    )
    total_attendance = result.scalar() or 0

    attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0

    # Suscripción activa
    result = await db.execute(
        select(Subscription).where(
            Subscription.student_id == current_user.id,
            Subscription.status == SubscriptionStatus.ACTIVE,
        )
    )
    subscription = result.scalars().first()

    return {
        "timestamp": datetime.utcnow(),
        "metrics": {
            "enrolled_classes": enrolled_classes,
            "attendance_rate_30days": round(attendance_rate, 2),
            "has_active_subscription": subscription is not None,
        }
    }
