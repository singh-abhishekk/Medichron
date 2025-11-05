"""
Contact form schemas.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class ContactBase(BaseModel):
    """Base contact schema."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    message: str = Field(..., min_length=10, max_length=2000)


class ContactCreate(ContactBase):
    """Schema for creating a contact form submission."""

    pass


class ContactInDB(ContactBase):
    """Schema for contact in database."""

    id: int
    created_at: datetime
    is_resolved: int

    class Config:
        from_attributes = True


class Contact(ContactInDB):
    """Schema for contact response."""

    pass
