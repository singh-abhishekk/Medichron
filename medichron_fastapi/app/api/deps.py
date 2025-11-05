"""
API dependencies for authentication and authorization.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.doctor import Doctor
from app.crud import user as crud_user
from app.crud import doctor as crud_doctor
from app.schemas.token import TokenPayload


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current authenticated user (patient).

    Args:
        db: Database session
        token: JWT token from request

    Returns:
        Current user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenPayload(**payload)
    except JWTError:
        raise credentials_exception

    user = crud_user.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


def get_current_doctor(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Doctor:
    """
    Get current authenticated doctor.

    Args:
        db: Database session
        token: JWT token from request

    Returns:
        Current doctor object

    Raises:
        HTTPException: If token is invalid or doctor not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenPayload(**payload)
    except JWTError:
        raise credentials_exception

    doctor = crud_doctor.get_doctor_by_username(db, username=username)
    if doctor is None:
        raise credentials_exception
    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Inactive doctor")

    return doctor


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        Current active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_doctor(
    current_doctor: Doctor = Depends(get_current_doctor)
) -> Doctor:
    """
    Get current active doctor.

    Args:
        current_doctor: Current doctor from token

    Returns:
        Current active doctor

    Raises:
        HTTPException: If doctor is inactive
    """
    if not current_doctor.is_active:
        raise HTTPException(status_code=400, detail="Inactive doctor")
    return current_doctor
