"""Model de Asistencia"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Text
from datetime import datetime
import enum

from ..database import Base


class AttendanceStatus(str, enum.Enum):
    """Estados de asistencia"""
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED = "excused"


class Attendance(Base):
    """Modelo de Asistencia"""

    __tablename__ = "attendance"

    id = Column(String(36), primary_key=True, index=True)
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    class_session_id = Column(
        String(36), ForeignKey("class_sessions.id"), nullable=False
    )
    marked_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    notes = Column(Text, nullable=True)

    marked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Attendance student={self.student_id} status={self.status}>"
