from datetime import datetime
from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from cryptography.fernet import Fernet
from functools import wraps
import qrcode
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medichron.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Encryption key for Aadhaar - MUST be set in environment
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    # Generate key for first run - save this to env!
    ENCRYPTION_KEY = Fernet.generate_key()
    print(f"WARNING: Generated new encryption key. Set this in environment:")
    print(f"export ENCRYPTION_KEY='{ENCRYPTION_KEY.decode()}'")
    print("Data encrypted with this key will be lost on restart if not set!")

cipher = Fernet(ENCRYPTION_KEY if isinstance(ENCRYPTION_KEY, bytes) else ENCRYPTION_KEY.encode())


# Validation functions
def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain number"
    return True, "Valid"


def validate_phone(phone):
    """Validate phone number."""
    return phone.isdigit() and len(phone) >= 10


def validate_aadhaar(aadhaar):
    """Validate Aadhaar number."""
    return aadhaar.isdigit() and len(aadhaar) == 12


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('log'))
        return f(*args, **kwargs)
    return decorated_function


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    date_of_birth = db.Column(db.String(20))
    aadhaar_encrypted = db.Column(db.LargeBinary, nullable=False)
    phone = db.Column(db.String(15))
    uid = db.Column(db.String(50), unique=True, nullable=False)


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    date_of_birth = db.Column(db.String(20))
    aadhaar_encrypted = db.Column(db.LargeBinary, nullable=False)
    phone = db.Column(db.String(15))


class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15))
    message = db.Column(db.Text, nullable=False)


# Initialize database
with app.app_context():
    db.create_all()


# Routes
@app.route('/')
@app.route('/index')
def home():
    return render_template("index.html")


@app.route('/contact', methods=['GET', 'POST'])
def cont():
    if request.method == 'POST':
        contact = Contact(
            first_name=request.form['firstname'],
            last_name=request.form['lastname'],
            email=request.form['email'],
            phone=request.form.get('phone'),
            message=request.form['messege']
        )
        db.session.add(contact)
        db.session.commit()
    return render_template("contact.html")


@app.route('/register', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('psw', '')
        phone = request.form.get('phone', '').strip()
        aadhaar = request.form.get('aadhaar', '').strip()

        # Validation
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters', 'error')
            return render_template('register.html')

        if not validate_email(email):
            flash('Invalid email format', 'error')
            return render_template('register.html')

        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'error')
            return render_template('register.html')

        if not validate_phone(phone):
            flash('Invalid phone number (minimum 10 digits)', 'error')
            return render_template('register.html')

        if not validate_aadhaar(aadhaar):
            flash('Invalid Aadhaar number (must be 12 digits)', 'error')
            return render_template('register.html')

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')

        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Encrypt Aadhaar
        aadhaar_encrypted = cipher.encrypt(aadhaar.encode())

        # Generate UID
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        uid = f"{first_name[0]}{last_name[0]}{phone[-4:]}{aadhaar[-4:]}"

        try:
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                location=request.form.get('location', ''),
                date_of_birth=request.form.get('dateofbirth', ''),
                aadhaar_encrypted=aadhaar_encrypted,
                phone=phone,
                uid=uid
            )

            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect('/login')
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/doctor', methods=['GET', 'POST'])
def doc():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('psw', '')
        phone = request.form.get('phone', '').strip()
        aadhaar = request.form.get('aadhaar', '').strip()

        # Validation
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters', 'error')
            return render_template('doctor.html')

        if not validate_email(email):
            flash('Invalid email format', 'error')
            return render_template('doctor.html')

        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'error')
            return render_template('doctor.html')

        if not validate_phone(phone):
            flash('Invalid phone number (minimum 10 digits)', 'error')
            return render_template('doctor.html')

        if not validate_aadhaar(aadhaar):
            flash('Invalid Aadhaar number (must be 12 digits)', 'error')
            return render_template('doctor.html')

        # Check if doctor exists
        if Doctor.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('doctor.html')

        if Doctor.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('doctor.html')

        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Encrypt Aadhaar
        aadhaar_encrypted = cipher.encrypt(aadhaar.encode())

        try:
            doctor = Doctor(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=request.form['firstname'],
                last_name=request.form['lastname'],
                location=request.form.get('location', ''),
                date_of_birth=request.form.get('dateofbirth', ''),
                aadhaar_encrypted=aadhaar_encrypted,
                phone=phone
            )

            db.session.add(doctor)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect('/login')
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('doctor.html')

    return render_template('doctor.html')


@app.route('/login', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password required', 'error')
            return render_template('login.html')

        # Check if doctor
        if 'check' in request.form:
            doctor = Doctor.query.filter_by(username=username).first()
            if doctor and bcrypt.check_password_hash(doctor.password_hash, password):
                session['username'] = username
                session['user_type'] = 'doctor'
                return redirect(f'/dashboardDoc/{username}')
            flash('Invalid credentials', 'error')
        else:
            # Check user
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password_hash, password):
                session['username'] = username
                session['user_type'] = 'patient'
                return redirect(f'/dashboardUser/{username}')
            flash('Invalid credentials', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout user and clear session."""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('log'))


@app.route('/dashboardUser/<username>', methods=['GET', 'POST'])
@login_required
def dashboard(username):
    # Verify user can only access their own dashboard
    if session.get('username') != username or session.get('user_type') != 'patient':
        flash('Unauthorized access', 'error')
        return redirect(url_for('log'))

    user = User.query.filter_by(username=username).first_or_404()

    if request.method == 'POST':
        if 'click' in request.form:
            return redirect(f'/qrgenerate/{username}')
        if 'hist' in request.form:
            return redirect(f'/userhistory/{username}')

    # Decrypt Aadhaar for display
    try:
        aadhaar = cipher.decrypt(user.aadhaar_encrypted).decode()
    except Exception:
        aadhaar = "****"  # Mask if decryption fails

    return render_template(
        "dashboardUser.html",
        username=user.username,
        firstname=user.first_name,
        lastname=user.last_name,
        location=user.location,
        dateofbirth=user.date_of_birth,
        email=user.email,
        phone=user.phone,
        aadhaar=aadhaar
    )


@app.route('/dashboardDoc/<username>')
@login_required
def dashboarddoc(username):
    # Verify doctor can only access their own dashboard
    if session.get('username') != username or session.get('user_type') != 'doctor':
        flash('Unauthorized access', 'error')
        return redirect(url_for('log'))

    doctor = Doctor.query.filter_by(username=username).first_or_404()

    # Decrypt Aadhaar for display
    try:
        aadhaar = cipher.decrypt(doctor.aadhaar_encrypted).decode()
    except Exception:
        aadhaar = "****"  # Mask if decryption fails

    return render_template(
        "dashboardDoc.html",
        username=doctor.username,
        firstname=doctor.first_name,
        lastname=doctor.last_name,
        location=doctor.location,
        dateofbirth=doctor.date_of_birth,
        email=doctor.email,
        phone=doctor.phone,
        aadhaar=aadhaar
    )


@app.route('/doctorhistory/<username>', methods=['GET', 'POST'])
@login_required
def history(username):
    # Only doctors can add medical records
    if session.get('user_type') != 'doctor':
        flash('Unauthorized access', 'error')
        return redirect(url_for('log'))

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(f'/userhistory/{username}')

        # Validate inputs
        symptoms = request.form.get('symptoms', '').strip()
        diagnosis = request.form.get('diagnosis', '').strip()
        treatment = request.form.get('treatment', '').strip()

        if not symptoms or not diagnosis or not treatment:
            flash('All fields are required', 'error')
            return render_template('historyDoctor.html', username=username)

        try:
            now = datetime.now()
            record = MedicalRecord(
                username=username,
                date=now.strftime('%Y-%m-%d'),
                time=now.strftime('%H:%M:%S'),
                symptoms=symptoms,
                diagnosis=diagnosis,
                treatment=treatment
            )
            db.session.add(record)
            db.session.commit()
            flash('Medical record added successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to add medical record', 'error')

    return render_template('historyDoctor.html', username=username)


@app.route('/userhistory/<username>', methods=['GET', 'POST'])
@login_required
def userhistory(username):
    # Users can only view their own history
    if session.get('username') != username and session.get('user_type') != 'doctor':
        flash('Unauthorized access', 'error')
        return redirect(url_for('log'))

    if request.method == 'POST':
        if 'pogo' in request.form:
            return redirect(f'/doctorhistory/{username}')

    records = MedicalRecord.query.filter_by(username=username).order_by(MedicalRecord.date.desc()).all()
    data = [[r.username, r.date, r.time, r.symptoms, r.diagnosis, r.treatment] for r in records]

    return render_template("historyUser.html", data=data)


@app.route('/qrgenerate/<username>')
@login_required
def gen(username):
    # Users can only generate their own QR code
    if session.get('username') != username or session.get('user_type') != 'patient':
        flash('Unauthorized access', 'error')
        return redirect(url_for('log'))

    user = User.query.filter_by(username=username).first_or_404()
    uid = user.uid

    save_directory = "static/qr_code"
    os.makedirs(save_directory, exist_ok=True)

    file_path = os.path.join(save_directory, f"{uid}.png")
    if not os.path.isfile(file_path):
        try:
            qr_code = qrcode.QRCode(version=1, box_size=10, border=5)
            qr_code.add_data(uid)
            qr_code.make(fit=True)
            img = qr_code.make_image(fill_color="black", back_color="white")
            img.save(file_path)
        except Exception as e:
            flash('Failed to generate QR code', 'error')
            return redirect(f'/dashboardUser/{username}')

    full_path = f"qr_code/{uid}.png"
    return render_template("qrgenerate.html", username=username, uid=uid, full_path=full_path)


@app.route('/scan')
def scan():
    # QR scanning functionality - requires camera integration
    pass


if __name__ == '__main__':
    app.run(debug=True)
