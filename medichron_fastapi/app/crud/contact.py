"""
CRUD operations for Contact model.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.contact import ContactCreate


def get_contact(db: Session, contact_id: int) -> Optional[Contact]:
    """Get contact by ID."""
    return db.query(Contact).filter(Contact.id == contact_id).first()


def get_contacts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    resolved_only: bool = False,
    pending_only: bool = False
) -> List[Contact]:
    """Get all contacts with optional filtering."""
    query = db.query(Contact)

    if resolved_only:
        query = query.filter(Contact.is_resolved == 1)
    elif pending_only:
        query = query.filter(Contact.is_resolved == 0)

    return query.order_by(Contact.created_at.desc()).offset(skip).limit(limit).all()


def create_contact(db: Session, contact: ContactCreate) -> Contact:
    """Create a new contact form submission."""
    db_contact = Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        message=contact.message
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def mark_contact_resolved(db: Session, contact_id: int) -> Optional[Contact]:
    """Mark a contact as resolved."""
    db_contact = get_contact(db, contact_id)
    if not db_contact:
        return None

    db_contact.is_resolved = 1
    db.commit()
    db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int) -> bool:
    """Delete a contact."""
    db_contact = get_contact(db, contact_id)
    if not db_contact:
        return False

    db.delete(db_contact)
    db.commit()
    return True
