"""Model de Estudiante"""

from sqlalchemy import Column, String, Date, ForeignKey, DateTime
from sqlalchemy.sql import func
from datetime import datetime

from ..database import Base


class Student(Base):
    """Modelo de Estudiante (extensión de User)"""

    __tablename__ = "students"

    id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<Student {self.id}>"
