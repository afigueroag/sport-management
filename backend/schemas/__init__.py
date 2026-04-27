"""Schemas package - Pydantic models for request/response validation"""

from .user import UserCreate, UserLogin, UserResponse, UserUpdate
from .student import StudentCreate, StudentResponse, StudentUpdate
from .auth import TokenResponse, RefreshTokenRequest
from .class_schema import ClassCreate, ClassResponse, ClassUpdate
from .enrollment_schema import EnrollmentCreate, EnrollmentResponse, EnrollmentUpdate
from .attendance_schema import AttendanceCreate, AttendanceResponse, AttendanceUpdate

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "StudentCreate",
    "StudentResponse",
    "StudentUpdate",
    "TokenResponse",
    "RefreshTokenRequest",
    "ClassCreate",
    "ClassResponse",
    "ClassUpdate",
    "EnrollmentCreate",
    "EnrollmentResponse",
    "EnrollmentUpdate",
    "AttendanceCreate",
    "AttendanceResponse",
    "AttendanceUpdate",
]
