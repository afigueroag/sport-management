"""Model de Clase"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Time,
    Boolean,
    ForeignKey,
    DateTime,
    Enum,
)
from datetime import datetime, time
import enum

from database import Base


class DayOfWeek(str, enum.Enum):
    """Días de la semana"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class Class(Base):
    """Modelo de Clase"""

    __tablename__ = "classes"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sport_type = Column(String(100), nullable=False)  # karate, pilates, natacion, etc
    instructor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    capacity = Column(Integer, default=20, nullable=False)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<Class {self.name}>"


class ClassSession(Base):
    """Modelo de Sesión de Clase (instancia específica de una clase)"""

    __tablename__ = "class_sessions"

    id = Column(String(36), primary_key=True, index=True)
    class_id = Column(String(36), ForeignKey("classes.id"), nullable=False)
    session_date = Column(DateTime, nullable=False)
    is_canceled = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ClassSession class_id={self.class_id} date={self.session_date}>"
