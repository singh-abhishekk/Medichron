# Migration Guide: Flask to FastAPI

This document explains the differences between the original Flask application and the new FastAPI implementation.

## Overview

The Medichron application has been completely restructured from Flask to FastAPI, following modern best practices and industry standards.

## Key Differences

### 1. Framework Change

**Original (Flask)**:
```python
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")
```

**New (FastAPI)**:
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome"}
```

### 2. Data Storage

| Aspect | Original | New |
|--------|----------|-----|
| Storage | CSV files | SQLAlchemy Database (SQLite/PostgreSQL) |
| Concurrency | File locks, race conditions | Database transactions |
| Scalability | Limited | High |
| Data Integrity | Manual validation | Database constraints |

**Original**:
```python
with open('nameListUser.csv', 'a', newline='') as inFile:
    writer = csv.DictWriter(inFile, fieldnames=fieldnames)
    writer.writerow({...})
```

**New**:
```python
db_user = User(username=user.username, ...)
db.add(db_user)
db.commit()
```

### 3. Authentication

| Feature | Original | New |
|---------|----------|-----|
| Method | Session-based | JWT tokens |
| Password Storage | Plaintext in CSV | Bcrypt hashed in DB |
| Security | Low | High |
| Stateless | No | Yes |

**Original**:
```python
if row[1] == username and row[7] == password:
    return redirect('/dashboard')
```

**New**:
```python
if not verify_password(password, user.hashed_password):
    raise HTTPException(status_code=401)
access_token = create_access_token(subject=user.username)
```

### 4. Request Validation

**Original**: Manual validation
```python
username = request.form["username"]
# No validation, potential security issues
```

**New**: Automatic validation with Pydantic
```python
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)
```

### 5. API Structure

**Original**: Template-based web application
- HTML templates rendered server-side
- Forms with POST/GET
- No API endpoints

**New**: RESTful API
- JSON request/response
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Automatic OpenAPI documentation
- Can serve any frontend (React, Vue, Mobile apps)

### 6. Project Structure

**Original**:
```
Medichron_instance1/
├── app.py (all code in one file)
├── templates/
├── static/
└── *.csv files
```

**New**:
```
medichron_fastapi/
├── app/
│   ├── api/         # API routes
│   ├── core/        # Config, security, database
│   ├── models/      # Database models
│   ├── schemas/     # Request/response schemas
│   ├── crud/        # Database operations
│   └── utils/       # Helper functions
├── tests/           # Test suite
└── static/          # Static files
```

### 7. Error Handling

**Original**:
```python
error = 'Invalid Credentials. Please try again.'
flash(error, "error")
```

**New**:
```python
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password"
)
```

### 8. Documentation

**Original**: No API documentation

**New**:
- Automatic OpenAPI/Swagger documentation
- Interactive API testing interface
- ReDoc alternative documentation

## Feature Comparison

| Feature | Original | New | Notes |
|---------|----------|-----|-------|
| User Registration | ✅ | ✅ | Improved validation |
| User Login | ✅ | ✅ | JWT-based |
| Doctor Registration | ✅ | ✅ | Improved validation |
| Doctor Login | ✅ | ✅ | JWT-based |
| Patient Dashboard | ✅ | 🔄 | API only (frontend separate) |
| Doctor Dashboard | ✅ | 🔄 | API only (frontend separate) |
| Medical Records | ✅ | ✅ | Enhanced with proper DB |
| QR Code Generation | ✅ | ✅ | Same functionality |
| QR Code Scanning | ✅ | ✅ | API endpoint |
| Contact Form | ✅ | ✅ | Improved |
| Password Security | ❌ | ✅ | Bcrypt hashing |
| Input Validation | ❌ | ✅ | Pydantic schemas |
| API Documentation | ❌ | ✅ | Auto-generated |
| Database | CSV | ✅ | SQLAlchemy |
| Tests | ❌ | ✅ | Pytest suite |
| Docker Support | ❌ | ✅ | Dockerfile + compose |

## Breaking Changes

### 1. No Server-Side Rendering
The new API doesn't render HTML templates. You need a separate frontend application (React, Vue, etc.) or use the API with tools like Postman.

### 2. Authentication Required
All protected endpoints now require JWT token authentication:

```bash
# Get token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass","user_type":"patient"}' \
  | jq -r '.access_token')

# Use token
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/users/me"
```

### 3. Data Migration Required
CSV data needs to be migrated to the database. Create a migration script if you have existing data.

### 4. Different URLs
- Original: `/register`, `/login`, `/dashboard`
- New: `/api/v1/auth/register/user`, `/api/v1/auth/login`, `/api/v1/users/me`

## Advantages of New Implementation

1. **Better Security**
   - Bcrypt password hashing
   - JWT authentication
   - Input validation
   - SQL injection protection

2. **Scalability**
   - Database instead of CSV
   - Stateless authentication
   - Can handle concurrent users
   - Easy to add caching

3. **Maintainability**
   - Organized code structure
   - Type hints
   - Automatic validation
   - Better error messages

4. **Developer Experience**
   - Interactive API documentation
   - Automatic request/response validation
   - Better IDE support
   - Easier testing

5. **Modern Architecture**
   - RESTful API
   - Separation of concerns
   - Can support multiple frontends
   - Mobile app ready

## Migration Steps

If you have existing data in CSV files:

1. **Backup Original Data**
   ```bash
   cp -r Medichron_instance1 Medichron_backup
   ```

2. **Create Migration Script**
   ```python
   # migrate_data.py
   import csv
   from app.crud import user, doctor
   from app.schemas.user import UserCreate
   # ... migration logic
   ```

3. **Run Migration**
   ```bash
   python migrate_data.py
   ```

4. **Verify Data**
   - Check database records
   - Test login functionality
   - Verify medical records

## Frontend Integration

To build a frontend for this API:

1. **Use the OpenAPI spec**
   - Available at: http://localhost:8000/openapi.json
   - Generate client SDK automatically

2. **Authentication Flow**
   ```javascript
   // Login
   const response = await fetch('/api/v1/auth/login', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({username, password, user_type: 'patient'})
   });
   const {access_token} = await response.json();

   // Store token
   localStorage.setItem('token', access_token);

   // Use token
   const userData = await fetch('/api/v1/users/me', {
     headers: {'Authorization': `Bearer ${access_token}`}
   });
   ```

3. **Recommended Frontend Frameworks**
   - React + TypeScript
   - Vue 3 + TypeScript
   - Angular
   - Svelte

## Questions?

For questions about the migration or new features, please refer to:
- README.md - Setup and usage instructions
- /docs - Interactive API documentation
- tests/test_api.py - Example API usage
