"""Schemas para Autenticación"""

from pydantic import BaseModel
from ..schemas.user import UserResponse


class TokenResponse(BaseModel):
    """Schema de respuesta con tokens JWT"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "juan@example.com",
                    "full_name": "Juan García",
                    "role": "student",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2026-04-27T12:00:00",
                },
            }
        }


class RefreshTokenRequest(BaseModel):
    """Schema para refrescar token"""
    refresh_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }
