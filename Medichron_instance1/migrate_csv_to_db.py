"""
Migrate CSV data to SQLite database with encryption.
Run once to import existing data.
"""
import csv
import os
from app_secure import app, db, User, Doctor, MedicalRecord, Contact, bcrypt, cipher


def migrate_users():
    """Migrate users from CSV to database."""
    try:
        with open('nameListUser.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if User.query.filter_by(username=row['username']).first():
                    continue

                user = User(
                    username=row['username'],
                    email=row['email'],
                    password_hash=bcrypt.generate_password_hash(row['password']).decode('utf-8'),
                    first_name=row['firstname'],
                    last_name=row['lastname'],
                    location=row['location'],
                    date_of_birth=row['dateofbirth'],
                    aadhaar_encrypted=cipher.encrypt(row['aadhaar'].encode()),
                    phone=row['phone'],
                    uid=row['uid']
                )
                db.session.add(user)
        db.session.commit()
        print("✓ Users migrated")
    except FileNotFoundError:
        print("✗ nameListUser.csv not found")
    except Exception as e:
        print(f"✗ User migration failed: {e}")
        db.session.rollback()


def migrate_doctors():
    """Migrate doctors from CSV to database."""
    try:
        with open('nameListDoc.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if Doctor.query.filter_by(username=row['username']).first():
                    continue

                doctor = Doctor(
                    username=row['username'],
                    email=row['email'],
                    password_hash=bcrypt.generate_password_hash(row['password']).decode('utf-8'),
                    first_name=row['firstname'],
                    last_name=row['lastname'],
                    location=row['location'],
                    date_of_birth=row['dateofbirth'],
                    aadhaar_encrypted=cipher.encrypt(row['aadhaar'].encode()),
                    phone=row['phone']
                )
                db.session.add(doctor)
        db.session.commit()
        print("✓ Doctors migrated")
    except FileNotFoundError:
        print("✗ nameListDoc.csv not found")
    except Exception as e:
        print(f"✗ Doctor migration failed: {e}")
        db.session.rollback()


def migrate_medical_records():
    """Migrate medical records from CSV to database."""
    try:
        with open('userhistory.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = MedicalRecord(
                    username=row['username'],
                    date=row['date'],
                    time=row['time'],
                    symptoms=row['symptoms'],
                    diagnosis=row['diagnosis'],
                    treatment=row['treatment']
                )
                db.session.add(record)
        db.session.commit()
        print("✓ Medical records migrated")
    except FileNotFoundError:
        print("✗ userhistory.csv not found")
    except Exception as e:
        print(f"✗ Medical records migration failed: {e}")
        db.session.rollback()


def migrate_contacts():
    """Migrate contacts from CSV to database."""
    try:
        with open('contact.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contact = Contact(
                    first_name=row['firstname'],
                    last_name=row['lastname'],
                    email=row['email'],
                    phone=row.get('phone'),
                    message=row['messege']  # Note: typo in original
                )
                db.session.add(contact)
        db.session.commit()
        print("✓ Contacts migrated")
    except FileNotFoundError:
        print("✗ contact.csv not found")
    except Exception as e:
        print(f"✗ Contact migration failed: {e}")
        db.session.rollback()


if __name__ == '__main__':
    with app.app_context():
        print("Starting migration...")
        migrate_users()
        migrate_doctors()
        migrate_medical_records()
        migrate_contacts()
        print("\nMigration complete!")
