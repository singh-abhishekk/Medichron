"""
CRUD operations for Doctor model.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from app.core.security import get_password_hash, verify_password


def get_doctor(db: Session, doctor_id: int) -> Optional[Doctor]:
    """Get doctor by ID."""
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()


def get_doctor_by_username(db: Session, username: str) -> Optional[Doctor]:
    """Get doctor by username."""
    return db.query(Doctor).filter(Doctor.username == username).first()


def get_doctor_by_email(db: Session, email: str) -> Optional[Doctor]:
    """Get doctor by email."""
    return db.query(Doctor).filter(Doctor.email == email).first()


def get_doctors(db: Session, skip: int = 0, limit: int = 100) -> List[Doctor]:
    """Get list of doctors with pagination."""
    return db.query(Doctor).offset(skip).limit(limit).all()


def create_doctor(db: Session, doctor: DoctorCreate) -> Doctor:
    """Create a new doctor."""
    db_doctor = Doctor(
        username=doctor.username,
        email=doctor.email,
        hashed_password=get_password_hash(doctor.password),
        first_name=doctor.first_name,
        last_name=doctor.last_name,
        location=doctor.location,
        date_of_birth=doctor.date_of_birth,
        aadhaar=doctor.aadhaar,  # In production, this should be encrypted
        phone=doctor.phone,
        specialization=doctor.specialization,
        license_number=doctor.license_number
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def update_doctor(
    db: Session,
    doctor_id: int,
    doctor_update: DoctorUpdate
) -> Optional[Doctor]:
    """Update doctor information."""
    db_doctor = get_doctor(db, doctor_id)
    if not db_doctor:
        return None

    update_data = doctor_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_doctor, field, value)

    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def delete_doctor(db: Session, doctor_id: int) -> bool:
    """Delete a doctor (soft delete by setting is_active to False)."""
    db_doctor = get_doctor(db, doctor_id)
    if not db_doctor:
        return False

    db_doctor.is_active = False
    db.commit()
    return True


def authenticate_doctor(
    db: Session,
    username: str,
    password: str
) -> Optional[Doctor]:
    """Authenticate a doctor with username and password."""
    doctor = get_doctor_by_username(db, username)
    if not doctor:
        return None
    if not verify_password(password, doctor.hashed_password):
        return None
    return doctor
