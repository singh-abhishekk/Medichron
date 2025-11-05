"""
Pytest configuration and fixtures for testing.
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.doctor import Doctor

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("TestPass123"),
        first_name="Test",
        last_name="User",
        location="Test City",
        date_of_birth=date(1990, 1, 1),
        aadhaar="123456789012",
        phone="1234567890",
        uid="TU7890789012"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    # Make transient to keep loaded attributes after session closes
    make_transient(user)
    return user


@pytest.fixture
def test_doctor(db_session):
    """Create a test doctor."""
    doctor = Doctor(
        username="testdoctor",
        email="doctor@example.com",
        hashed_password=get_password_hash("DoctorPass123"),
        first_name="Test",
        last_name="Doctor",
        location="Hospital",
        date_of_birth=date(1985, 1, 1),
        aadhaar="987654321098",
        phone="9876543210",
        specialization="General Medicine"
    )
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    # Make transient to keep loaded attributes after session closes
    make_transient(doctor)
    return doctor


@pytest.fixture
def user_token(client, test_user):
    """Get authentication token for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "TestPass123",
            "user_type": "patient"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def doctor_token(client, test_doctor):
    """Get authentication token for test doctor."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testdoctor",
            "password": "DoctorPass123",
            "user_type": "doctor"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers_user(user_token):
    """Get authorization headers for user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def auth_headers_doctor(doctor_token):
    """Get authorization headers for doctor."""
    return {"Authorization": f"Bearer {doctor_token}"}
