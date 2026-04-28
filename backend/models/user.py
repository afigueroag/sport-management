"""Model de Usuario"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    """Roles de usuario"""
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"
    RECEPTIONIST = "receptionist"


class User(Base):
    """Modelo de Usuario"""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
