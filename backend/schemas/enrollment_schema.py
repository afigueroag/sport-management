"""Enrollment schemas for request/response validation"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from models.enrollment import EnrollmentStatus


class EnrollmentCreate(BaseModel):
    """Schema para crear una inscripción"""
    student_id: str
    class_id: str


class EnrollmentUpdate(BaseModel):
    """Schema para actualizar una inscripción"""
    status: Optional[EnrollmentStatus] = None


class EnrollmentResponse(BaseModel):
    """Schema para responder con datos de inscripción"""
    id: str
    student_id: str
    class_id: str
    status: EnrollmentStatus
    enrolled_at: datetime
    canceled_at: Optional[datetime]

    class Config:
        from_attributes = True
