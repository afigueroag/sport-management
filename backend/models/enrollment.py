"""Model de Inscripción"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Enum
from datetime import datetime
import enum

from ..database import Base


class EnrollmentStatus(str, enum.Enum):
    """Estados de inscripción"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELED = "canceled"


class Enrollment(Base):
    """Modelo de Inscripción (Student ↔ Class)"""

    __tablename__ = "enrollments"

    id = Column(String(36), primary_key=True, index=True)
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    class_id = Column(String(36), ForeignKey("classes.id"), nullable=False)
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)

    enrolled_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    canceled_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Enrollment student={self.student_id} class={self.class_id}>"
