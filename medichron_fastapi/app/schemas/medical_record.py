"""
Medical Record Pydantic schemas for request/response validation.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MedicalRecordBase(BaseModel):
    """Base medical record schema."""

    symptoms: Optional[str] = Field(None, max_length=2000)
    diagnosis: Optional[str] = Field(None, max_length=2000)
    treatment: Optional[str] = Field(None, max_length=2000)
    notes: Optional[str] = Field(None, max_length=5000)


class MedicalRecordCreate(MedicalRecordBase):
    """Schema for creating a new medical record."""

    patient_id: int
    doctor_id: int


class MedicalRecordUpdate(BaseModel):
    """Schema for updating a medical record."""

    symptoms: Optional[str] = Field(None, max_length=2000)
    diagnosis: Optional[str] = Field(None, max_length=2000)
    treatment: Optional[str] = Field(None, max_length=2000)
    notes: Optional[str] = Field(None, max_length=5000)


class MedicalRecordInDB(MedicalRecordBase):
    """Schema for medical record in database."""

    id: int
    patient_id: int
    doctor_id: int
    visit_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicalRecord(MedicalRecordInDB):
    """Schema for medical record response."""

    pass


class MedicalRecordWithDetails(MedicalRecord):
    """Schema for medical record with patient and doctor details."""

    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
