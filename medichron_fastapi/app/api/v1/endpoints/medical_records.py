"""
Medical record endpoints for patient visit history.
"""
from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_doctor
from app.crud import medical_record as crud_medical_record
from app.schemas.medical_record import (
    MedicalRecord,
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordWithDetails
)
from app.models.user import User
from app.models.doctor import Doctor

router = APIRouter()


@router.post("/", response_model=MedicalRecord, status_code=status.HTTP_201_CREATED)
def create_medical_record(
    record_in: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    """
    Create a new medical record (doctors only).

    Args:
        record_in: Medical record data
        db: Database session
        current_doctor: Current authenticated doctor

    Returns:
        Created medical record

    Raises:
        HTTPException: If doctor ID doesn't match current doctor
    """
    # Ensure the doctor creating the record is the authenticated doctor
    if record_in.doctor_id != current_doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create medical records for other doctors"
        )

    record = crud_medical_record.create_medical_record(db, record=record_in)
    return record


@router.get("/patient/{patient_id}", response_model=List[MedicalRecord])
def read_patient_medical_records(
    patient_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get medical records for a specific patient (patients can only view own records).

    Args:
        patient_id: Patient ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of medical records

    Raises:
        HTTPException: If patient tries to access another patient's records
    """
    # Patients can only access their own records
    if current_user.id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other patients' medical records"
        )

    records = crud_medical_record.get_medical_records_by_patient(
        db,
        patient_id=patient_id,
        skip=skip,
        limit=limit
    )
    return records


@router.get("/patient/me", response_model=List[MedicalRecord])
def read_my_medical_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get medical records for current patient.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of medical records
    """
    records = crud_medical_record.get_medical_records_by_patient(
        db,
        patient_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return records


@router.get("/doctor/{doctor_id}", response_model=List[MedicalRecord])
def read_doctor_medical_records(
    doctor_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    """
    Get medical records created by a specific doctor.

    Args:
        doctor_id: Doctor ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_doctor: Current authenticated doctor

    Returns:
        List of medical records
    """
    records = crud_medical_record.get_medical_records_by_doctor(
        db,
        doctor_id=doctor_id,
        skip=skip,
        limit=limit
    )
    return records


@router.get("/doctor/me", response_model=List[MedicalRecord])
def read_my_doctor_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    """
    Get medical records created by current doctor.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_doctor: Current authenticated doctor

    Returns:
        List of medical records
    """
    records = crud_medical_record.get_medical_records_by_doctor(
        db,
        doctor_id=current_doctor.id,
        skip=skip,
        limit=limit
    )
    return records


@router.get("/{record_id}", response_model=MedicalRecord)
def read_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific medical record (patients can only view their own records).

    Args:
        record_id: Medical record ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Medical record data

    Raises:
        HTTPException: If record not found or unauthorized
    """
    record = crud_medical_record.get_medical_record(db, record_id=record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )

    # Patients can only view their own medical records
    if record.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other patients' medical records"
        )

    return record


@router.put("/{record_id}", response_model=MedicalRecord)
def update_medical_record(
    record_id: int,
    record_in: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    """
    Update a medical record (doctors only).

    Args:
        record_id: Medical record ID
        record_in: Updated medical record data
        db: Database session
        current_doctor: Current authenticated doctor

    Returns:
        Updated medical record

    Raises:
        HTTPException: If record not found or doctor not authorized
    """
    # Get existing record
    existing_record = crud_medical_record.get_medical_record(db, record_id=record_id)
    if not existing_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )

    # Ensure the doctor updating the record is the one who created it
    if existing_record.doctor_id != current_doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update medical records created by other doctors"
        )

    record = crud_medical_record.update_medical_record(
        db,
        record_id=record_id,
        record_update=record_in
    )
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    """
    Delete a medical record (doctors only).

    Args:
        record_id: Medical record ID
        db: Database session
        current_doctor: Current authenticated doctor

    Returns:
        None

    Raises:
        HTTPException: If record not found or doctor not authorized
    """
    # Get existing record
    existing_record = crud_medical_record.get_medical_record(db, record_id=record_id)
    if not existing_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )

    # Ensure the doctor deleting the record is the one who created it
    if existing_record.doctor_id != current_doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete medical records created by other doctors"
        )

    crud_medical_record.delete_medical_record(db, record_id=record_id)
    return None
