"""
QR code endpoints for patient identification.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import user as crud_user
from app.schemas.user import User

router = APIRouter()


@router.get("/scan/{uid}", response_model=User)
def scan_qr_code(
    uid: str,
    db: Session = Depends(get_db)
):
    """
    Get patient information by scanning QR code (UID).

    This endpoint simulates the QR code scanning functionality.
    In the original app, a camera scans the QR code and extracts the UID.

    Args:
        uid: Unique identifier from QR code
        db: Database session

    Returns:
        User data

    Raises:
        HTTPException: If user not found
    """
    user = crud_user.get_user_by_uid(db, uid=uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this QR code"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user account is inactive"
        )

    return user
