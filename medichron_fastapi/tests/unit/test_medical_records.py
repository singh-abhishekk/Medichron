"""
Unit tests for medical records endpoints and authorization fixes.
"""
import pytest
from fastapi import status


class TestMedicalRecordCreation:
    """Test medical record creation (doctors only)."""

    def test_create_medical_record_as_doctor(
        self, client, test_user, test_doctor, auth_headers_doctor
    ):
        """Test doctor can create medical records."""
        response = client.post(
            "/api/v1/medical-records/",
            json={
                "patient_id": test_user.id,
                "doctor_id": test_doctor.id,
                "symptoms": "Fever and headache",
                "diagnosis": "Common cold",
                "treatment": "Rest and fluids"
            },
            headers=auth_headers_doctor
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["patient_id"] == test_user.id
        assert data["doctor_id"] == test_doctor.id

    def test_create_medical_record_unauthorized(
        self, client, test_user, auth_headers_user
    ):
        """Test patients cannot create medical records."""
        response = client.post(
            "/api/v1/medical-records/",
            json={
                "patient_id": test_user.id,
                "doctor_id": 999,
                "symptoms": "Test",
                "diagnosis": "Test",
                "treatment": "Test"
            },
            headers=auth_headers_user
        )
        # Should fail because endpoint requires doctor auth
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_record_for_other_doctor(
        self, client, test_user, test_doctor, auth_headers_doctor
    ):
        """Test doctor cannot create records for other doctors."""
        response = client.post(
            "/api/v1/medical-records/",
            json={
                "patient_id": test_user.id,
                "doctor_id": 999,  # Different doctor
                "symptoms": "Test",
                "diagnosis": "Test",
                "treatment": "Test"
            },
            headers=auth_headers_doctor
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestMedicalRecordAuthorization:
    """Test authorization fixes for medical records."""

    def test_patient_access_own_records(
        self, client, test_user, auth_headers_user
    ):
        """Test patient can access their own records (Bug Fix #3)."""
        response = client.get(
            f"/api/v1/medical-records/patient/{test_user.id}",
            headers=auth_headers_user
        )
        assert response.status_code == status.HTTP_200_OK

    def test_patient_cannot_access_other_records(
        self, client, test_user, auth_headers_user
    ):
        """Test patient cannot access other patient's records (Bug Fix #2)."""
        response = client.get(
            "/api/v1/medical-records/patient/999",  # Different patient
            headers=auth_headers_user
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "cannot access" in response.json()["detail"].lower()

    def test_get_record_by_id_requires_auth(self, client, db_session, test_user):
        """Test getting record by ID requires authentication (Bug Fix #3)."""
        # Create a record first
        from app.models.medical_record import MedicalRecord
        record = MedicalRecord(
            patient_id=test_user.id,
            doctor_id=1,
            symptoms="Test",
            diagnosis="Test",
            treatment="Test"
        )
        db_session.add(record)
        db_session.commit()

        # Try without auth
        response = client.get(f"/api/v1/medical-records/{record.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_record_by_id_owns_record(
        self, client, db_session, test_user, auth_headers_user
    ):
        """Test patient can only view their own record by ID."""
        from app.models.medical_record import MedicalRecord

        # Create record for test user
        record = MedicalRecord(
            patient_id=test_user.id,
            doctor_id=1,
            symptoms="Test",
            diagnosis="Test",
            treatment="Test"
        )
        db_session.add(record)
        db_session.commit()

        response = client.get(
            f"/api/v1/medical-records/{record.id}",
            headers=auth_headers_user
        )
        assert response.status_code == status.HTTP_200_OK

    def test_get_record_by_id_not_owner(
        self, client, db_session, test_user, auth_headers_user
    ):
        """Test patient cannot view others' records by ID."""
        from app.models.medical_record import MedicalRecord

        # Create record for different patient
        record = MedicalRecord(
            patient_id=999,  # Different patient
            doctor_id=1,
            symptoms="Test",
            diagnosis="Test",
            treatment="Test"
        )
        db_session.add(record)
        db_session.commit()

        response = client.get(
            f"/api/v1/medical-records/{record.id}",
            headers=auth_headers_user
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestMedicalRecordCRUD:
    """Test CRUD operations on medical records."""

    def test_get_my_medical_records(
        self, client, test_user, auth_headers_user
    ):
        """Test getting current user's medical records."""
        response = client.get(
            "/api/v1/medical-records/patient/me",
            headers=auth_headers_user
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_update_medical_record_as_creator(
        self, client, db_session, test_doctor, auth_headers_doctor
    ):
        """Test doctor can update their own created records."""
        from app.models.medical_record import MedicalRecord

        record = MedicalRecord(
            patient_id=1,
            doctor_id=test_doctor.id,
            symptoms="Original",
            diagnosis="Original",
            treatment="Original"
        )
        db_session.add(record)
        db_session.commit()

        response = client.put(
            f"/api/v1/medical-records/{record.id}",
            json={"symptoms": "Updated symptoms"},
            headers=auth_headers_doctor
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["symptoms"] == "Updated symptoms"

    def test_delete_medical_record_as_creator(
        self, client, db_session, test_doctor, auth_headers_doctor
    ):
        """Test doctor can delete their own created records."""
        from app.models.medical_record import MedicalRecord

        record = MedicalRecord(
            patient_id=1,
            doctor_id=test_doctor.id,
            symptoms="Test",
            diagnosis="Test",
            treatment="Test"
        )
        db_session.add(record)
        db_session.commit()

        response = client.delete(
            f"/api/v1/medical-records/{record.id}",
            headers=auth_headers_doctor
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
