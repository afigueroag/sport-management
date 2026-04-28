"""Class schemas for request/response validation"""

from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import Optional
from ..models.class_model import DayOfWeek


class ClassCreate(BaseModel):
    """Schema para crear una nueva clase"""
    name: str = Field(..., min_length=2, max_length=255)
    sport_type: str = Field(..., min_length=2, max_length=100)
    capacity: int = Field(default=20, ge=1, le=200)
    day_of_week: DayOfWeek
    start_time: time
    end_time: time


class ClassUpdate(BaseModel):
    """Schema para actualizar una clase"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    sport_type: Optional[str] = Field(None, min_length=2, max_length=100)
    capacity: Optional[int] = Field(None, ge=1, le=200)
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_active: Optional[bool] = None


class ClassResponse(BaseModel):
    """Schema para responder con datos de clase"""
    id: str
    name: str
    sport_type: str
    instructor_id: str
    capacity: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
