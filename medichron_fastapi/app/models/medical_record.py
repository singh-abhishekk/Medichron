"""
Medical Record database model.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class MedicalRecord(Base):
    """Medical record model for patient visit history."""

    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    visit_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    symptoms = Column(Text)
    diagnosis = Column(Text)
    treatment = Column(Text)
    notes = Column(Text)  # Additional notes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")
