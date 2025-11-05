"""
Integration tests for complete user flows.
"""
import pytest
from fastapi import status


class TestPatientJourney:
    """Test complete patient journey through the system."""

    def test_patient_registration_to_qr_code(self, client):
        """Test patient can register, login, and get QR code."""
        # Step 1: Register
        register_response = client.post(
            "/api/v1/auth/register/user",
            json={
                "username": "patient1",
                "email": "patient1@example.com",
                "password": "Patient123",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "1234567890",
                "aadhaar": "123456789012",
                "location": "New York",
                "date_of_birth": "1990-01-01"
            }
        )
        assert register_response.status_code == status.HTTP_201_CREATED
        user_data = register_response.json()

        # Step 2: Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "patient1",
                "password": "Patient123",
                "user_type": "patient"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Get user profile
        profile_response = client.get("/api/v1/users/me", headers=headers)
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.json()["username"] == "patient1"

        # Step 4: Get QR code
        qr_response = client.get("/api/v1/users/me/qr-code", headers=headers)
        assert qr_response.status_code == status.HTTP_200_OK
        assert "qr_code_url" in qr_response.json()

    def test_patient_cannot_see_other_patients_data(self, client, test_user):
        """Test patient isolation - cannot access other patient data."""
        # Create and login as patient 1
        login1 = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "TestPass123",
                "user_type": "patient"
            }
        )
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Register patient 2
        client.post(
            "/api/v1/auth/register/user",
            json={
                "username": "patient2",
                "email": "patient2@example.com",
                "password": "Patient123",
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "9876543210",
                "aadhaar": "987654321098"
            }
        )

        # Login as patient 2
        login2 = client.post(
            "/api/v1/auth/login",
            json={
                "username": "patient2",
                "password": "Patient123",
                "user_type": "patient"
            }
        )
        patient2_data = login2.json()

        # Get patient2 profile to get their ID
        token2 = patient2_data["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        patient2_profile = client.get("/api/v1/users/me", headers=headers2)
        patient2_id = patient2_profile.json()["id"]

        # Patient 1 tries to access patient 2's records
        response = client.get(
            f"/api/v1/medical-records/patient/{patient2_id}",
            headers=headers1
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDoctorPatientFlow:
    """Test doctor-patient interactions."""

    def test_doctor_creates_and_views_medical_record(
        self, client, test_user, test_doctor
    ):
        """Test complete flow: doctor creates record, patient views it."""
        # Doctor login
        doctor_login = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testdoctor",
                "password": "DoctorPass123",
                "user_type": "doctor"
            }
        )
        doctor_token = doctor_login.json()["access_token"]
        doctor_headers = {"Authorization": f"Bearer {doctor_token}"}

        # Doctor creates medical record
        create_response = client.post(
            "/api/v1/medical-records/",
            json={
                "patient_id": test_user.id,
                "doctor_id": test_doctor.id,
                "symptoms": "Fever, cough",
                "diagnosis": "Flu",
                "treatment": "Rest and medication"
            },
            headers=doctor_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        record = create_response.json()

        # Patient login
        patient_login = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "TestPass123",
                "user_type": "patient"
            }
        )
        patient_token = patient_login.json()["access_token"]
        patient_headers = {"Authorization": f"Bearer {patient_token}"}

        # Patient views their medical records
        view_response = client.get(
            "/api/v1/medical-records/patient/me",
            headers=patient_headers
        )
        assert view_response.status_code == status.HTTP_200_OK
        records = view_response.json()
        assert len(records) == 1
        assert records[0]["symptoms"] == "Fever, cough"

        # Patient views specific record
        record_response = client.get(
            f"/api/v1/medical-records/{record['id']}",
            headers=patient_headers
        )
        assert record_response.status_code == status.HTTP_200_OK
        assert record_response.json()["diagnosis"] == "Flu"


class TestContactForm:
    """Test contact form functionality."""

    def test_contact_form_submission(self, client):
        """Test anyone can submit contact form."""
        response = client.post(
            "/api/v1/contact/",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "1234567890",
                "message": "This is a test message for the contact form."
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "john@example.com"
        assert "id" in data
