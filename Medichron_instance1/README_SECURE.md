# Secure Flask Implementation

## Changes from Original

### Security Fixes
1. **Password Hashing**: Bcrypt replaces plaintext storage
2. **Aadhaar Encryption**: Fernet (AES-256) encrypts sensitive PII
3. **SQLite Database**: Replaces CSV files for data integrity
4. **Environment Variables**: Secrets in env vars, not code

### Setup

```bash
# Install dependencies
pip install -r requirements_secure.txt

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set environment variables
export SECRET_KEY="your-secret-key-here"
export ENCRYPTION_KEY="key-from-above"

# Run application
python app_secure.py
```

### Key Features

**Database Models**:
- `User`: Patients with encrypted Aadhaar
- `Doctor`: Healthcare providers with encrypted Aadhaar
- `MedicalRecord`: Visit history
- `Contact`: Contact form submissions

**Password Security**:
- Bcrypt with salt (auto-generated per password)
- Verify with `check_password_hash()`
- No plaintext storage

**Aadhaar Encryption**:
- Fernet symmetric encryption (AES-256)
- Encrypted at rest in database
- Decrypted only when needed for display

### First Principles

**Why Bcrypt?**
- Designed to be slow (prevents brute-force)
- Automatic salt generation
- Computationally expensive

**Why Fernet?**
- Symmetric encryption (fast)
- Built on industry standards (AES + HMAC)
- Need to decrypt for verification/display

**Why SQLite?**
- ACID compliance
- Concurrent read access
- Data integrity with constraints
