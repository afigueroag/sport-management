"""Schemas para Estudiante"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date

from ..schemas.user import UserResponse


class StudentCreate(BaseModel):
    """Schema para crear estudiante"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "maria@example.com",
                "password": "securepassword123",
                "full_name": "María López",
                "phone": "+52555123456",
                "date_of_birth": "1990-05-15",
                "emergency_contact_name": "Juan López",
                "emergency_contact_phone": "+52555654321",
            }
        }


class StudentUpdate(BaseModel):
    """Schema para actualizar estudiante"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+52555123456",
                "emergency_contact_name": "Juan López",
            }
        }


class StudentResponse(BaseModel):
    """Schema de respuesta para estudiante"""
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "maria@example.com",
                "full_name": "María López",
                "phone": "+52555123456",
                "date_of_birth": "1990-05-15",
                "emergency_contact_name": "Juan López",
                "emergency_contact_phone": "+52555654321",
                "created_at": "2026-04-27T12:00:00",
            }
        }
