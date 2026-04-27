"""Class Session schemas for request/response validation"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ClassSessionCreate(BaseModel):
    """Schema para crear una sesión de clase"""
    class_id: str
    session_date: datetime


class ClassSessionUpdate(BaseModel):
    """Schema para actualizar una sesión de clase"""
    session_date: Optional[datetime] = None
    is_canceled: Optional[bool] = None


class ClassSessionResponse(BaseModel):
    """Schema para responder con datos de sesión de clase"""
    id: str
    class_id: str
    session_date: datetime
    is_canceled: bool
    created_at: datetime

    class Config:
        from_attributes = True
