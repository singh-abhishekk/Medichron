"""
Authentication endpoints for login and registration.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.crud import user as crud_user
from app.crud import doctor as crud_doctor
from app.schemas.token import Token, LoginRequest
from app.schemas.user import UserCreate, User
from app.schemas.doctor import DoctorCreate, Doctor

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint for users and doctors.

    Args:
        login_data: Login credentials (username, password, user_type)
        db: Database session

    Returns:
        Access token

    Raises:
        HTTPException: If credentials are invalid
    """
    if login_data.user_type == "doctor":
        user = crud_doctor.authenticate_doctor(
            db,
            username=login_data.username,
            password=login_data.password
        )
    else:  # Default to patient
        user = crud_user.authenticate_user(
            db,
            username=login_data.username,
            password=login_data.password
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username,
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login (for Swagger UI).

    Args:
        db: Database session
        form_data: OAuth2 form data

    Returns:
        Access token
    """
    # Try to authenticate as user first, then as doctor
    user = crud_user.authenticate_user(
        db,
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        user = crud_doctor.authenticate_doctor(
            db,
            username=form_data.username,
            password=form_data.password
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username,
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register/user", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user (patient).

    Args:
        user_in: User registration data
        db: Database session

    Returns:
        Created user

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    user = crud_user.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = crud_user.create_user(db, user=user_in)
    return user


@router.post("/register/doctor", response_model=Doctor, status_code=status.HTTP_201_CREATED)
def register_doctor(
    doctor_in: DoctorCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new doctor.

    Args:
        doctor_in: Doctor registration data
        db: Database session

    Returns:
        Created doctor

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    doctor = crud_doctor.get_doctor_by_username(db, username=doctor_in.username)
    if doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    doctor = crud_doctor.get_doctor_by_email(db, email=doctor_in.email)
    if doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new doctor
    doctor = crud_doctor.create_doctor(db, doctor=doctor_in)
    return doctor
