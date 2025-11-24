from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None


class UserCreate(UserBase):
    password: str

    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ClientPreferences(BaseModel):
    workout_program: Optional[str] = None
    preferred_time: Optional[str] = None
    goals: Optional[str] = None


class ClientResponse(BaseModel):
    id: int
    user: UserResponse
    preferences: Dict[str, Any]
    join_date: datetime

    class Config:
        from_attributes = True