"""
CRUD operations for User model.
"""
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from loguru import logger

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_uid(db: Session, uid: str) -> Optional[User]:
    """Get user by UID."""
    return db.query(User).filter(User.uid == uid).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    # Generate secure UID using UUID4
    uid = str(uuid.uuid4())

    try:
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password),
            first_name=user.first_name,
            last_name=user.last_name,
            location=user.location,
            date_of_birth=user.date_of_birth,
            aadhaar=user.aadhaar,  # TODO: Encrypt this field
            phone=user.phone,
            uid=uid
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User created: {user.username}")
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create user {user.username}: {str(e)}")
        raise


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user information."""
    db_user = get_user(db, user_id)
    if not db_user:
        logger.warning(f"User not found for update: {user_id}")
        return None

    try:
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        logger.info(f"User updated: {user_id}")
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update user {user_id}: {str(e)}")
        raise


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user (soft delete by setting is_active to False)."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    db_user.is_active = False
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
