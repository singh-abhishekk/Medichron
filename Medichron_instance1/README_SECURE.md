# Secure Flask Implementation

## Critical Fixes from Bot Review

### 1. Encryption Key Bug (CRITICAL)
**Issue**: Key regenerated on each restart → data loss
**Fix**: Warning displayed if not set, guides user to save key

### 2. Security Enhancements
- Input validation (email, password, phone, Aadhaar)
- Session management with `@login_required`
- Authorization checks (users can't access others' data)
- Error handling with try-catch blocks
- CSRF protection via Flask sessions

## Changes from Original

### Security Fixes
1. **Password Hashing**: Bcrypt replaces plaintext
2. **Aadhaar Encryption**: Fernet (AES-256) for PII
3. **SQLite Database**: Replaces CSV files
4. **Input Validation**: Email, password strength, Aadhaar format
5. **Session Management**: Login required, authorization checks
6. **Error Handling**: Graceful failures with user feedback

### Setup

```bash
# Install
pip install -r requirements_secure.txt

# Generate keys (SAVE THESE!)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set environment
export SECRET_KEY="$(openssl rand -hex 32)"
export ENCRYPTION_KEY="key-from-above"

# Run
python app_secure.py
```

**WARNING**: App displays encryption key on first run. SAVE IT to environment variable or all encrypted data becomes unreadable on restart!

### Validation Rules

**Password**:
- Minimum 8 characters
- Must contain: uppercase, lowercase, digit

**Email**: Standard format validation

**Phone**: Minimum 10 digits, numeric only

**Aadhaar**: Exactly 12 digits, numeric only

### Authorization Model

**Patient**:
- View own dashboard
- View own medical history
- Generate own QR code

**Doctor**:
- View own dashboard
- Add medical records for patients
- View patient medical history

**Session Protection**:
- All protected routes require login
- Users can't access other users' data
- Automatic redirect to login if unauthorized

### Database Models

**User** (Patients):
- Encrypted Aadhaar
- Hashed password
- Unique UID for QR codes

**Doctor**:
- Encrypted Aadhaar
- Hashed password
- Same security as users

**MedicalRecord**:
- Linked to patient username
- Timestamped entries
- Symptoms, diagnosis, treatment

**Contact**:
- Public contact form
- No authentication required

### First Principles

**Why Bcrypt?**
- Adaptive work factor (can increase difficulty)
- Auto-salted (different hash per password)
- Slow by design (brute-force resistant)

**Why Fernet?**
- Symmetric (fast encrypt/decrypt)
- AES-256 + HMAC authentication
- Reversible (needed for Aadhaar display)

**Why SQLite?**
- ACID transactions
- Concurrent reads
- Referential integrity

**Why Sessions?**
- Server-side storage (secure)
- Automatic CSRF protection
- Easy authorization checks
