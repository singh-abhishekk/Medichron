"""
User endpoints for patient operations.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_active_user
from app.crud import user as crud_user
from app.schemas.user import User, UserUpdate, UserWithQR
from app.models.user import User as UserModel
from app.utils.qr_generator import generate_qr_code, qr_code_exists, get_qr_code_path

router = APIRouter()


@router.get("/me", response_model=User)
def read_user_me(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user data
    """
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update current user information.

    Args:
        user_in: Updated user data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated user data
    """
    user = crud_user.update_user(db, user_id=current_user.id, user_update=user_in)
    return user


@router.get("/me/qr-code", response_model=UserWithQR)
def get_user_qr_code(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get QR code for current user.

    Args:
        current_user: Current authenticated user

    Returns:
        User data with QR code URL
    """
    # Check if QR code already exists
    if not qr_code_exists(current_user.uid):
        # Generate new QR code
        qr_path = generate_qr_code(current_user.uid, current_user.uid)
    else:
        qr_path = get_qr_code_path(current_user.uid)

    # Create response with QR code URL
    user_data = User.model_validate(current_user)
    return UserWithQR(**user_data.model_dump(), qr_code_url=f"/{qr_path}")


@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get user by ID.

    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        User data

    Raises:
        HTTPException: If user not found
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/", response_model=List[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get list of users.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of users
    """
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Delete (deactivate) current user account.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        None
    """
    crud_user.delete_user(db, user_id=current_user.id)
    return None
