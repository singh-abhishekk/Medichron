"""
CRUD operations for Medical Record model.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.medical_record import MedicalRecord
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate


def get_medical_record(db: Session, record_id: int) -> Optional[MedicalRecord]:
    """Get medical record by ID."""
    return db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()


def get_medical_records_by_patient(
    db: Session,
    patient_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[MedicalRecord]:
    """Get all medical records for a specific patient."""
    return db.query(MedicalRecord).filter(
        MedicalRecord.patient_id == patient_id
    ).order_by(MedicalRecord.visit_date.desc()).offset(skip).limit(limit).all()


def get_medical_records_by_doctor(
    db: Session,
    doctor_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[MedicalRecord]:
    """Get all medical records created by a specific doctor."""
    return db.query(MedicalRecord).filter(
        MedicalRecord.doctor_id == doctor_id
    ).order_by(MedicalRecord.visit_date.desc()).offset(skip).limit(limit).all()


def get_all_medical_records(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[MedicalRecord]:
    """Get all medical records with pagination."""
    return db.query(MedicalRecord).order_by(
        MedicalRecord.visit_date.desc()
    ).offset(skip).limit(limit).all()


def create_medical_record(
    db: Session,
    record: MedicalRecordCreate
) -> MedicalRecord:
    """Create a new medical record."""
    db_record = MedicalRecord(
        patient_id=record.patient_id,
        doctor_id=record.doctor_id,
        symptoms=record.symptoms,
        diagnosis=record.diagnosis,
        treatment=record.treatment,
        notes=record.notes
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def update_medical_record(
    db: Session,
    record_id: int,
    record_update: MedicalRecordUpdate
) -> Optional[MedicalRecord]:
    """Update a medical record."""
    db_record = get_medical_record(db, record_id)
    if not db_record:
        return None

    update_data = record_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)

    db.commit()
    db.refresh(db_record)
    return db_record


def delete_medical_record(db: Session, record_id: int) -> bool:
    """Delete a medical record."""
    db_record = get_medical_record(db, record_id)
    if not db_record:
        return False

    db.delete(db_record)
    db.commit()
    return True
