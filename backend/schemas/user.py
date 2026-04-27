"""Schemas para Usuario"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from models.user import UserRole


class UserCreate(BaseModel):
    """Schema para crear usuario"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Contraseña mínimo 8 caracteres")
    full_name: str = Field(..., min_length=2, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan@example.com",
                "password": "securepassword123",
                "full_name": "Juan García",
            }
        }


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan@example.com",
                "password": "securepassword123",
            }
        }


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    password: Optional[str] = Field(None, min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Juan Carlos García",
            }
        }


class UserResponse(BaseModel):
    """Schema de respuesta para usuario"""
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "juan@example.com",
                "full_name": "Juan García",
                "role": "student",
                "is_active": True,
                "is_verified": False,
                "created_at": "2026-04-27T12:00:00",
            }
        }
