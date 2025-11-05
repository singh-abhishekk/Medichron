"""
Basic API tests for Medichron FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_read_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert response.json()["name"] == "Medichron API"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_register_user():
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register/user",
        json={
            "username": "testuser123",
            "email": "test@example.com",
            "password": "TestPass123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "9876543210",
            "aadhaar": "123456789012",
            "location": "Test City",
            "date_of_birth": "1990-01-01"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser123"
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_register_duplicate_user():
    """Test registering duplicate user."""
    # First registration
    client.post(
        "/api/v1/auth/register/user",
        json={
            "username": "duplicate123",
            "email": "duplicate@example.com",
            "password": "TestPass123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "9876543211",
            "aadhaar": "123456789013",
        }
    )

    # Duplicate registration
    response = client.post(
        "/api/v1/auth/register/user",
        json={
            "username": "duplicate123",
            "email": "different@example.com",
            "password": "TestPass123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "9876543212",
            "aadhaar": "123456789014",
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_user():
    """Test user login."""
    # Register user first
    client.post(
        "/api/v1/auth/register/user",
        json={
            "username": "logintest",
            "email": "login@example.com",
            "password": "TestPass123",
            "first_name": "Login",
            "last_name": "Test",
            "phone": "9876543213",
            "aadhaar": "123456789015",
        }
    )

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "logintest",
            "password": "TestPass123",
            "user_type": "patient"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "WrongPass123",
            "user_type": "patient"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_get_current_user():
    """Test getting current user profile."""
    # Register and login
    client.post(
        "/api/v1/auth/register/user",
        json={
            "username": "currentuser",
            "email": "current@example.com",
            "password": "TestPass123",
            "first_name": "Current",
            "last_name": "User",
            "phone": "9876543214",
            "aadhaar": "123456789016",
        }
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "currentuser",
            "password": "TestPass123",
            "user_type": "patient"
        }
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"
    assert data["email"] == "current@example.com"


def test_unauthorized_access():
    """Test accessing protected endpoint without token."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_contact_form_submission():
    """Test contact form submission."""
    response = client.post(
        "/api/v1/contact/",
        json={
            "first_name": "Contact",
            "last_name": "Test",
            "email": "contact@example.com",
            "phone": "9876543215",
            "message": "This is a test contact message that is long enough."
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Contact"
    assert data["email"] == "contact@example.com"


# Cleanup
@pytest.fixture(scope="session", autouse=True)
def cleanup():
    """Cleanup test database after tests."""
    yield
    # Cleanup code can go here if needed
