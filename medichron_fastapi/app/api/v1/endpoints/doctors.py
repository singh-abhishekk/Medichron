"""
Doctor endpoints for healthcare provider operations.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_doctor, get_current_active_doctor
from app.crud import doctor as crud_doctor
from app.schemas.doctor import Doctor, DoctorUpdate
from app.models.doctor import Doctor as DoctorModel

router = APIRouter()


@router.get("/me", response_model=Doctor)
def read_doctor_me(
    current_doctor: DoctorModel = Depends(get_current_active_doctor)
):
    """
    Get current doctor information.

    Args:
        current_doctor: Current authenticated doctor

    Returns:
        Current doctor data
    """
    return current_doctor


@router.put("/me", response_model=Doctor)
def update_doctor_me(
    doctor_in: DoctorUpdate,
    db: Session = Depends(get_db),
    current_doctor: DoctorModel = Depends(get_current_active_doctor)
):
    """
    Update current doctor information.

    Args:
        doctor_in: Updated doctor data
        db: Database session
        current_doctor: Current authenticated doctor

    Returns:
        Updated doctor data
    """
    doctor = crud_doctor.update_doctor(
        db,
        doctor_id=current_doctor.id,
        doctor_update=doctor_in
    )
    return doctor


@router.get("/{doctor_id}", response_model=Doctor)
def read_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """
    Get doctor by ID.

    Args:
        doctor_id: Doctor ID
        db: Database session

    Returns:
        Doctor data

    Raises:
        HTTPException: If doctor not found
    """
    doctor = crud_doctor.get_doctor(db, doctor_id=doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    return doctor


@router.get("/", response_model=List[Doctor])
def read_doctors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of doctors.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of doctors
    """
    doctors = crud_doctor.get_doctors(db, skip=skip, limit=limit)
    return doctors


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor_me(
    db: Session = Depends(get_db),
    current_doctor: DoctorModel = Depends(get_current_active_doctor)
):
    """
    Delete (deactivate) current doctor account.

    Args:
        db: Database session
        current_doctor: Current authenticated doctor

    Returns:
        None
    """
    crud_doctor.delete_doctor(db, doctor_id=current_doctor.id)
    return None
