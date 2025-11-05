# Medichron API

A modern, RESTful healthcare management system built with FastAPI, featuring patient records management, doctor consultations, and QR code-based patient identification.

## Features

- **User Authentication**: Secure JWT-based authentication for both patients and doctors
- **Patient Management**: Complete CRUD operations for patient records
- **Doctor Management**: Healthcare provider profiles and management
- **Medical Records**: Track patient visits, symptoms, diagnoses, and treatments
- **QR Code Integration**: Generate and scan QR codes for quick patient identification
- **Contact Forms**: Patient inquiry and contact management
- **RESTful API**: Modern REST API with automatic OpenAPI documentation
- **Security**: Password hashing with bcrypt, JWT tokens, input validation
- **Database**: SQLAlchemy ORM with support for SQLite, PostgreSQL, and MySQL

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn with ASGI
- **Database**: SQLAlchemy 2.0 (ORM)
- **Authentication**: JWT (python-jose) + bcrypt
- **Validation**: Pydantic v2
- **QR Codes**: qrcode + Pillow
- **Python**: 3.8+

## Project Structure

```
medichron_fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── deps.py            # Dependencies (auth, db session)
│   │   └── v1/
│   │       ├── api.py         # API router
│   │       └── endpoints/
│   │           ├── auth.py           # Login, registration
│   │           ├── users.py          # Patient endpoints
│   │           ├── doctors.py        # Doctor endpoints
│   │           ├── medical_records.py # Medical history
│   │           ├── contact.py        # Contact forms
│   │           └── qr_codes.py       # QR scanning
│   ├── core/
│   │   ├── config.py          # Settings and configuration
│   │   ├── security.py        # Password hashing, JWT
│   │   └── database.py        # Database connection
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── medical_record.py
│   │   └── contact.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── medical_record.py
│   │   ├── contact.py
│   │   └── token.py
│   ├── crud/                  # Database operations
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── medical_record.py
│   │   └── contact.py
│   └── utils/                 # Utility functions
│       └── qr_generator.py
├── static/                    # Static files
├── tests/                     # Test suite
├── .env.example              # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd medichron_fastapi
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```

6. **Edit `.env` file** and configure:
   - `SECRET_KEY`: Generate a secure key (use `openssl rand -hex 32`)
   - `DATABASE_URL`: Database connection string
   - Other settings as needed

7. **Create required directories**:
   ```bash
   mkdir -p static/qr_codes static/uploads
   ```

## Running the Application

### Development Mode

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using the main.py script
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs - Interactive API documentation
- **ReDoc**: http://localhost:8000/redoc - Alternative API documentation

## API Endpoints Overview

### Authentication (`/api/v1/auth`)

- `POST /auth/login` - Login for users and doctors
- `POST /auth/login/token` - OAuth2 compatible login
- `POST /auth/register/user` - Register new patient
- `POST /auth/register/doctor` - Register new doctor

### Users/Patients (`/api/v1/users`)

- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `GET /users/me/qr-code` - Get QR code for current user
- `GET /users/{user_id}` - Get user by ID
- `GET /users/` - List all users
- `DELETE /users/me` - Deactivate account

### Doctors (`/api/v1/doctors`)

- `GET /doctors/me` - Get current doctor profile
- `PUT /doctors/me` - Update current doctor profile
- `GET /doctors/{doctor_id}` - Get doctor by ID
- `GET /doctors/` - List all doctors
- `DELETE /doctors/me` - Deactivate account

### Medical Records (`/api/v1/medical-records`)

- `POST /medical-records/` - Create medical record (doctors only)
- `GET /medical-records/patient/{patient_id}` - Get patient's records
- `GET /medical-records/patient/me` - Get my medical records
- `GET /medical-records/doctor/{doctor_id}` - Get doctor's records
- `GET /medical-records/doctor/me` - Get my created records
- `GET /medical-records/{record_id}` - Get specific record
- `PUT /medical-records/{record_id}` - Update record (doctors only)
- `DELETE /medical-records/{record_id}` - Delete record (doctors only)

### QR Codes (`/api/v1/qr`)

- `GET /qr/scan/{uid}` - Get patient info by QR code UID

### Contact (`/api/v1/contact`)

- `POST /contact/` - Submit contact form
- `GET /contact/` - List all contacts (admin)
- `GET /contact/{contact_id}` - Get specific contact
- `PATCH /contact/{contact_id}/resolve` - Mark as resolved (admin)
- `DELETE /contact/{contact_id}` - Delete contact (admin)

## Usage Examples

### Register a New Patient

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/user" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "9876543210",
    "aadhaar": "123456789012",
    "location": "New York",
    "date_of_birth": "1990-01-01"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123",
    "user_type": "patient"
  }'
```

### Get QR Code (with authentication)

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/qr-code" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create Medical Record (doctor only)

```bash
curl -X POST "http://localhost:8000/api/v1/medical-records/" \
  -H "Authorization: Bearer DOCTOR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "doctor_id": 1,
    "symptoms": "Fever, headache",
    "diagnosis": "Common cold",
    "treatment": "Rest and fluids, paracetamol as needed"
  }'
```

## Database Migrations

The application automatically creates database tables on startup. For production, consider using Alembic for migrations:

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create a migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Security Considerations

### Current Implementation

✅ Password hashing with bcrypt
✅ JWT token authentication
✅ Input validation with Pydantic
✅ CORS configuration
✅ SQL injection protection (SQLAlchemy ORM)

### Production Recommendations

⚠️ **Before deploying to production**:

1. **Change SECRET_KEY**: Use a strong, randomly generated key
2. **Use HTTPS**: Enable SSL/TLS certificates
3. **Database**: Migrate from SQLite to PostgreSQL
4. **Encrypt Aadhaar**: Encrypt sensitive PII data at rest
5. **Rate Limiting**: Implement rate limiting on endpoints
6. **Add Admin Role**: Implement role-based access control
7. **Logging**: Set up proper logging and monitoring
8. **Backup**: Implement database backup strategy
9. **Environment**: Set `DEBUG=False` in production
10. **Secrets Management**: Use proper secrets management (Vault, AWS Secrets, etc.)

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Development

### Code Style

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **mypy** for type checking

```bash
# Format code
black app/

# Lint
flake8 app/

# Type check
mypy app/
```

## Migration from Original Flask App

This FastAPI version is a complete restructure of the original Flask application with the following improvements:

### Major Changes

1. **Framework**: Flask → FastAPI
2. **Data Storage**: CSV files → SQLAlchemy database
3. **Authentication**: Basic auth → JWT tokens
4. **Security**: Plaintext passwords → Bcrypt hashing
5. **Validation**: Manual validation → Pydantic schemas
6. **Documentation**: None → Auto-generated OpenAPI docs
7. **Architecture**: Monolithic → Layered (MVC-like)

### Preserved Features

- User registration and login (patients and doctors)
- Medical record management
- QR code generation for patient identification
- Contact form submission
- Patient history tracking

### Original Code Backup

The original Flask application has been preserved in `medichron_original_backup.zip` in the root directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is for educational purposes.

## Support

For issues and questions, please create an issue in the repository.

## Acknowledgments

- Original Medichron Flask application
- FastAPI framework and documentation
- SQLAlchemy ORM
