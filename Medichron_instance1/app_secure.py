from datetime import datetime
from flask import Flask, render_template, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from cryptography.fernet import Fernet
import qrcode
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medichron.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Encryption key for Aadhaar - store in env in production
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
cipher = Fernet(ENCRYPTION_KEY)


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
        username = request.form['username']

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')

        # Hash password
        password_hash = bcrypt.generate_password_hash(request.form['psw']).decode('utf-8')

        # Encrypt Aadhaar
        aadhaar_encrypted = cipher.encrypt(request.form['aadhaar'].encode())

        # Generate UID
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        phone = request.form['phone']
        aadhaar = request.form['aadhaar']
        uid = f"{first_name[0]}{last_name[0]}{phone[-4:]}{aadhaar[-4:]}"

        user = User(
            username=username,
            email=request.form['email'],
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            location=request.form['location'],
            date_of_birth=request.form['dateofbirth'],
            aadhaar_encrypted=aadhaar_encrypted,
            phone=phone,
            uid=uid
        )

        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect('/login')

    return render_template('register.html')


@app.route('/doctor', methods=['GET', 'POST'])
def doc():
    if request.method == 'POST':
        username = request.form['username']

        # Check if doctor exists
        if Doctor.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('doctor.html')

        # Hash password
        password_hash = bcrypt.generate_password_hash(request.form['psw']).decode('utf-8')

        # Encrypt Aadhaar
        aadhaar_encrypted = cipher.encrypt(request.form['aadhaar'].encode())

        doctor = Doctor(
            username=username,
            email=request.form['email'],
            password_hash=password_hash,
            first_name=request.form['firstname'],
            last_name=request.form['lastname'],
            location=request.form['location'],
            date_of_birth=request.form['dateofbirth'],
            aadhaar_encrypted=aadhaar_encrypted,
            phone=request.form['phone']
        )

        db.session.add(doctor)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect('/login')

    return render_template('doctor.html')


@app.route('/login', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if doctor
        if 'check' in request.form:
            doctor = Doctor.query.filter_by(username=username).first()
            if doctor and bcrypt.check_password_hash(doctor.password_hash, password):
                return redirect(f'/dashboardDoc/{username}')
            flash('Invalid credentials', 'error')
        else:
            # Check user
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password_hash, password):
                return redirect(f'/dashboardUser/{username}')
            flash('Invalid credentials', 'error')

    return render_template('login.html')


@app.route('/dashboardUser/<username>', methods=['GET', 'POST'])
def dashboard(username):
    user = User.query.filter_by(username=username).first_or_404()

    if request.method == 'POST':
        if 'click' in request.form:
            return redirect(f'/qrgenerate/{username}')
        if 'hist' in request.form:
            return redirect(f'/userhistory/{username}')

    # Decrypt Aadhaar for display
    aadhaar = cipher.decrypt(user.aadhaar_encrypted).decode()

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
def dashboarddoc(username):
    doctor = Doctor.query.filter_by(username=username).first_or_404()

    # Decrypt Aadhaar for display
    aadhaar = cipher.decrypt(doctor.aadhaar_encrypted).decode()

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
def history(username):
    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(f'/userhistory/{username}')

        now = datetime.now()
        record = MedicalRecord(
            username=username,
            date=now.strftime('%Y-%m-%d'),
            time=now.strftime('%H:%M:%S'),
            symptoms=request.form['symptoms'],
            diagnosis=request.form['diagnosis'],
            treatment=request.form['treatment']
        )
        db.session.add(record)
        db.session.commit()

    return render_template('historyDoctor.html', username=username)


@app.route('/userhistory/<username>', methods=['GET', 'POST'])
def userhistory(username):
    if request.method == 'POST':
        if 'pogo' in request.form:
            return redirect(f'/doctorhistory/{username}')

    records = MedicalRecord.query.filter_by(username=username).all()
    data = [[r.username, r.date, r.time, r.symptoms, r.diagnosis, r.treatment] for r in records]

    return render_template("historyUser.html", data=data)


@app.route('/qrgenerate/<username>')
def gen(username):
    user = User.query.filter_by(username=username).first_or_404()
    uid = user.uid

    save_directory = "static/qr_code"
    os.makedirs(save_directory, exist_ok=True)

    file_path = os.path.join(save_directory, f"{uid}.png")
    if not os.path.isfile(file_path):
        qr_code = qrcode.QRCode(version=1, box_size=10, border=5)
        qr_code.add_data(uid)
        qr_code.make(fit=True)
        img = qr_code.make_image(fill_color="black", back_color="white")
        img.save(file_path)

    full_path = f"qr_code/{uid}.png"
    return render_template("qrgenerate.html", username=username, uid=uid, full_path=full_path)


@app.route('/scan')
def scan():
    # QR scanning functionality - requires camera integration
    pass


if __name__ == '__main__':
    app.run(debug=True)
