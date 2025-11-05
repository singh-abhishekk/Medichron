"""
Doctor Pydantic schemas for request/response validation.
"""
from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr, Field, field_validator


class DoctorBase(BaseModel):
    """Base doctor schema with common fields."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    specialization: Optional[str] = None


class DoctorCreate(DoctorBase):
    """Schema for creating a new doctor."""

    password: str = Field(..., min_length=8)
    aadhaar: str = Field(..., min_length=12, max_length=12)
    license_number: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @field_validator('aadhaar')
    @classmethod
    def validate_aadhaar(cls, v: str) -> str:
        """Validate Aadhaar number format."""
        if not v.isdigit():
            raise ValueError('Aadhaar must contain only digits')
        if len(v) != 12:
            raise ValueError('Aadhaar must be exactly 12 digits')
        return v


class DoctorUpdate(BaseModel):
    """Schema for updating doctor information."""

    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None


class DoctorInDB(DoctorBase):
    """Schema for doctor in database."""

    id: int
    is_active: bool
    license_number: Optional[str] = None

    class Config:
        from_attributes = True


class Doctor(DoctorInDB):
    """Schema for doctor response."""

    pass
