"""
Doctor database model.
"""
from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class Doctor(Base):
    """Doctor model for healthcare providers."""

    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    location = Column(String)
    date_of_birth = Column(Date)
    aadhaar = Column(String, unique=True)  # Should be encrypted in production
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    specialization = Column(String)  # e.g., Cardiology, Neurology, etc.
    license_number = Column(String, unique=True)  # Medical license number

    # Relationships
    medical_records = relationship("MedicalRecord", back_populates="doctor")
