from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'patient', 'hospital_staff', 'ngo_admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    notice_period = db.Column(db.Integer, default=7)
    last_visit = db.Column(db.DateTime)
    next_visit = db.Column(db.DateTime)
    disease = db.Column(db.String(100))
    current_medications = db.Column(db.Text)
    assigned_hospital = db.Column(db.String(100))
    patient_notes = db.Column(db.Text)

    user = db.relationship('User', backref=db.backref('patient', lazy=True, uselist=False))


class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    visit_type = db.Column(db.String(50))  # Regular, Emergency, Follow-up
    diagnosis = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    lab_results = db.Column(db.Text)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    next_visit = db.Column(db.DateTime)
    visit_notes = db.Column(db.Text)
    is_critical = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    is_urgent = db.Column(db.Boolean, default=False)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    departments = db.Column(db.Text)
    bed_capacity = db.Column(db.Integer)
    current_occupancy = db.Column(db.Integer)

class AssistanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approval_date = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20))  # medication, appointment, message, alert
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.String(10), default='normal')  # low, normal, high

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Doctor Information
    doctor_name = db.Column(db.String(100), nullable=False)
    medical_license = db.Column(db.String(50), nullable=False)
    hospital_name = db.Column(db.String(200), nullable=False)
    hospital_address = db.Column(db.Text, nullable=False)
    doctor_email = db.Column(db.String(120))
    doctor_phone = db.Column(db.String(20))
    
    # Patient Information (denormalized for quick access)
    patient_name = db.Column(db.String(100), nullable=False)
    patient_dob = db.Column(db.Date)
    patient_gender = db.Column(db.String(10))
    patient_address = db.Column(db.Text)
    patient_email = db.Column(db.String(120))
    patient_phone = db.Column(db.String(20))
    insurance_details = db.Column(db.Text)
    
    # Prescription Details (stored as JSON for flexibility)
    medicines = db.Column(db.JSON)  # [{medicine_name, dosage, frequency, duration, instructions}, ...]
    
    # Additional Information
    remarks = db.Column(db.Text)  # Precautions, notes
    doctor_signature = db.Column(db.String(200))
    prescription_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)

class LabRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Test Information
    test_name = db.Column(db.String(100), nullable=False)  # Blood Test, X-Ray, MRI, etc.
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Hospital Information
    hospital_name = db.Column(db.String(200), nullable=False)
    hospital_location = db.Column(db.Text)
    
    # Results
    results = db.Column(db.JSON)  # [{parameter, value, unit, normal_range, status}, ...]
    overall_status = db.Column(db.String(20), default='Pending')  # Normal, Abnormal, Pending
    
    # Additional Details
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    is_completed = db.Column(db.Boolean, default=False)

# Add relationships
#Patient.user = db.relationship('User', backref='patient_profile', foreign_keys=[Patient.user_id])
Patient.records = db.relationship('MedicalRecord', backref='patient', lazy='dynamic')
Patient.assistance = db.relationship('AssistanceRecord', backref='patient', lazy='dynamic')
Patient.prescriptions = db.relationship('Prescription', backref='patient', lazy='dynamic', foreign_keys=[Prescription.patient_id])
Patient.lab_records = db.relationship('LabRecord', backref='patient', lazy='dynamic', foreign_keys=[LabRecord.patient_id])
MedicalRecord.doctor = db.relationship('User', backref='medical_records', foreign_keys=[MedicalRecord.doctor_id])
Prescription.doctor = db.relationship('User', backref='prescriptions', foreign_keys=[Prescription.doctor_id])
#Prescription.patient = db.relationship('Patient', foreign_keys=[Prescription.patient_id])
LabRecord.doctor = db.relationship('User', backref='lab_records', foreign_keys=[LabRecord.doctor_id])
#LabRecord.patient = db.relationship('Patient', foreign_keys=[LabRecord.patient_id])
Message.sender = db.relationship('User', foreign_keys=[Message.sender_id], backref='sent_messages')
Message.receiver = db.relationship('User', foreign_keys=[Message.receiver_id], backref='received_messages')
