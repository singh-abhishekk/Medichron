"""
Contact form endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import contact as crud_contact
from app.schemas.contact import Contact, ContactCreate

router = APIRouter()


@router.post("/", response_model=Contact, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact_in: ContactCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a contact form.

    Args:
        contact_in: Contact form data
        db: Database session

    Returns:
        Created contact entry
    """
    contact = crud_contact.create_contact(db, contact=contact_in)
    return contact


@router.get("/", response_model=List[Contact])
def read_contacts(
    skip: int = 0,
    limit: int = 100,
    resolved: bool = None,
    db: Session = Depends(get_db)
):
    """
    Get all contact form submissions.

    Note: In production, this should be restricted to admin users only.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        resolved: Filter by resolved status (True/False/None for all)
        db: Database session

    Returns:
        List of contact submissions
    """
    if resolved is True:
        contacts = crud_contact.get_contacts(
            db,
            skip=skip,
            limit=limit,
            resolved_only=True
        )
    elif resolved is False:
        contacts = crud_contact.get_contacts(
            db,
            skip=skip,
            limit=limit,
            pending_only=True
        )
    else:
        contacts = crud_contact.get_contacts(db, skip=skip, limit=limit)

    return contacts


@router.get("/{contact_id}", response_model=Contact)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific contact submission.

    Args:
        contact_id: Contact ID
        db: Database session

    Returns:
        Contact data

    Raises:
        HTTPException: If contact not found
    """
    contact = crud_contact.get_contact(db, contact_id=contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


@router.patch("/{contact_id}/resolve", response_model=Contact)
def resolve_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark a contact as resolved.

    Note: In production, this should be restricted to admin users only.

    Args:
        contact_id: Contact ID
        db: Database session

    Returns:
        Updated contact data

    Raises:
        HTTPException: If contact not found
    """
    contact = crud_contact.mark_contact_resolved(db, contact_id=contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a contact submission.

    Note: In production, this should be restricted to admin users only.

    Args:
        contact_id: Contact ID
        db: Database session

    Returns:
        None

    Raises:
        HTTPException: If contact not found
    """
    success = crud_contact.delete_contact(db, contact_id=contact_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return None
