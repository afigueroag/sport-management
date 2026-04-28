"""Attendance schemas for request/response validation"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..models.attendance import AttendanceStatus


class AttendanceCreate(BaseModel):
    """Schema para marcar asistencia"""
    student_id: str
    class_session_id: str
    status: AttendanceStatus
    notes: Optional[str] = Field(None, max_length=500)


class AttendanceUpdate(BaseModel):
    """Schema para actualizar asistencia"""
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = Field(None, max_length=500)


class AttendanceResponse(BaseModel):
    """Schema para responder con datos de asistencia"""
    id: str
    student_id: str
    class_session_id: str
    marked_by: str
    status: AttendanceStatus
    notes: Optional[str]
    marked_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
