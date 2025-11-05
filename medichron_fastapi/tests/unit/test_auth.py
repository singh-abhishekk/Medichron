"""
Unit tests for authentication endpoints.
"""
import pytest
from fastapi import status


class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_user_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register/user",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "NewPass123",
                "first_name": "New",
                "last_name": "User",
                "phone": "1234567890",
                "aadhaar": "123456789012",
                "location": "Test City",
                "date_of_birth": "1995-05-15"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        response = client.post(
            "/api/v1/auth/register/user",
            json={
                "username": "testuser",  # Duplicate
                "email": "different@example.com",
                "password": "TestPass123",
                "first_name": "Test",
                "last_name": "User",
                "phone": "9876543210",
                "aadhaar": "987654321098"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        response = client.post(
            "/api/v1/auth/register/user",
            json={
                "username": "differentuser",
                "email": "test@example.com",  # Duplicate
                "password": "TestPass123",
                "first_name": "Test",
                "last_name": "User",
                "phone": "9876543210",
                "aadhaar": "987654321098"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register/user",
            json={
                "username": "testuser2",
                "email": "invalid-email",
                "password": "TestPass123",
                "first_name": "Test",
                "last_name": "User",
                "phone": "1234567890",
                "aadhaar": "123456789012"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDoctorRegistration:
    """Test doctor registration endpoint."""

    def test_register_doctor_success(self, client):
        """Test successful doctor registration."""
        response = client.post(
            "/api/v1/auth/register/doctor",
            json={
                "username": "newdoctor",
                "email": "newdoctor@example.com",
                "password": "DoctorPass123",
                "first_name": "New",
                "last_name": "Doctor",
                "phone": "1234567890",
                "aadhaar": "123456789012",
                "location": "Hospital",
                "date_of_birth": "1980-01-01",
                "specialization": "Cardiology"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newdoctor"
        assert "password" not in data


class TestLogin:
    """Test login endpoints."""

    def test_login_user_success(self, client, test_user):
        """Test successful user login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "TestPass123",
                "user_type": "patient"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_doctor_success(self, client, test_doctor):
        """Test successful doctor login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testdoctor",
                "password": "DoctorPass123",
                "user_type": "doctor"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data

    def test_login_invalid_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "WrongPass123",
                "user_type": "patient"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent username."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "SomePass123",
                "user_type": "patient"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_oauth2_flow(self, client, test_user):
        """Test OAuth2 compatible login."""
        response = client.post(
            "/api/v1/auth/login/token",
            data={
                "username": "testuser",
                "password": "TestPass123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
