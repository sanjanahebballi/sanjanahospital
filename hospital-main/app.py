from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models import db, User, Patient, MedicalRecord, Message, Hospital, Notification, Prescription, LabRecord
import os
import random
import string
from dotenv import load_dotenv





# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'development-key-replace-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Sanjana123@localhost/healthcare'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize db with app
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

ADMIN_EMAIL = "admin@hospital.com"

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    # Always redirect to login page, regardless of authentication
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        user = User.query.filter_by(email=email, role=role).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'hospital_admin':
                return redirect(url_for('hospital_dashboard'))
            elif user.role == 'patient':
                return redirect(url_for('patient_dashboard'))
            elif user.role == 'ngo_admin':
                return redirect(url_for('ngo_dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor_dashboard')) if 'doctor_dashboard' in globals() else redirect(url_for('dashboard'))
            else:
                return redirect(url_for('dashboard'))
        flash('Invalid email, password, or role', 'danger')
    return render_template('login.html')


def init_db():
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        admin = User.query.filter_by(email=ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=ADMIN_EMAIL,
                password=generate_password_hash('hospital123'),
                role='admin',
                name='Hospital Admin',
                is_verified=True
            )
            db.session.add(admin)
            db.session.commit()
        # Add fixed patient
        patient_user = User.query.filter_by(email='patient@gmail.com').first()
        if not patient_user:
            patient_user = User(
                email='patient@gmail.com',
                password=generate_password_hash('patient123'),
                role='patient',
                name='Patient',
                is_verified=True
            )
            db.session.add(patient_user)
            db.session.commit()
            patient = Patient(user_id=patient_user.id, notice_period=7)
            db.session.add(patient)
            db.session.commit()
        # Add fixed NGO admin
        ngo_user = User.query.filter_by(email='ngo@gmail.com').first()
        if not ngo_user:
            ngo_user = User(
                email='ngo@gmail.com',
                password=generate_password_hash('ngo123'),
                role='ngo_admin',
                name='NGO Admin',
                is_verified=True
            )
            db.session.add(ngo_user)
            db.session.commit()
        # Add 10 patients with different diseases if not already present
        if not Patient.query.first():
            diseases = ['Cancer', 'TB', 'AIDS', 'HIV']
            hospitals = ['City Hospital', 'Metro Hospital']
            for i in range(10):
                email = f'patient{i+1}@example.com'
                if not User.query.filter_by(email=email).first():
                    user = User(
                        email=email,
                        password_hash=generate_password_hash('password'),
                        role='patient',
                        name=f'Patient {i+1}',
                        is_verified=True
                    )
                    db.session.add(user)
                    db.session.commit()
                    patient = Patient(
                        user_id=user.id,
                        name=user.name,
                        notice_period=7 + (i % 4),
                        last_visit=datetime(2025, 6, 10 + i),
                        next_visit=datetime(2025, 7, 1 + i),
                        disease=diseases[i % 4]
                    )
                    db.session.add(patient)
            db.session.commit()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/verify_admin', methods=['GET', 'POST'])
def verify_admin():
    if request.method == 'POST':
        code = request.form.get('code')
        admin = User.query.filter_by(email=ADMIN_EMAIL).first()
        
        if admin and code == admin.verification_code:
            admin.is_verified = True
            admin.verification_code = None
            db.session.commit()
            login_user(admin)
            flash('Admin verified successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        flash('Invalid verification code', 'danger')
    return render_template('verify_admin.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')
            # Validate required fields
            if not all([name, email, password, role]):
                flash('All fields are required.', 'danger')
                return redirect(url_for('register'))
            # Prevent hospital_admin registration
            if role == 'hospital_admin':
                flash('Hospital registration is not allowed. Please use the fixed hospital login.', 'danger')
                return redirect(url_for('register'))
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash('Email address already registered.', 'danger')
                return redirect(url_for('register'))
            # Create new user
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(
                name=name,
                email=email,
                password=hashed_password,
                role=role,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            db.session.add(new_user)
            db.session.commit()
            # If the role is patient, create a patient record
            if role == 'patient':
                new_patient = Patient(
                    user_id=new_user.id,
                    notice_period=7,  # Default notice period
                )
                db.session.add(new_patient)
                db.session.commit()
            # If the role is ngo_admin, redirect to login page
            if role == 'ngo_admin':
                flash('NGO registered successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            # Default: patient registration, redirect to login
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")  # For debugging
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('register'))
    # GET request - show registration form
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin' or current_user.role == 'hospital_admin':
        patients = Patient.query.all()
        return render_template('admin_dashboard.html', user=current_user, patients=patients)
    elif current_user.role == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        return render_template('patient_dashboard.html', user=current_user, patient=patient)
    elif current_user.role == 'ngo_admin':
        patients = Patient.query.all()
        # Aggregate disease counts
        disease_counts = {d: 0 for d in ['Cancer', 'TB', 'AIDS', 'HIV']}
        for p in patients:
            if p.disease in disease_counts:
                disease_counts[p.disease] += 1
        ngo = {
            'name': 'Helping Hands',
            'pincode': '580020',
            'email': 'ngo@email.com',
            'address': 'Hubli City, Karnataka',
            'symbol': 'https://img.icons8.com/color/96/000000/charity.png'
        }
        return render_template('ngo_dashboard.html', user=current_user, patients=patients, disease_counts=disease_counts, ngo=ngo)
    else:
        # For any other role, redirect to login or show a generic dashboard
        flash('Access denied or dashboard not implemented for your role.', 'danger')
        return redirect(url_for('login'))

@app.route('/messages')
@login_required
def messages():
    received = Message.query.filter_by(receiver_id=current_user.id)\
        .order_by(Message.sent_at.desc()).all()
    sent = Message.query.filter_by(sender_id=current_user.id)\
        .order_by(Message.sent_at.desc()).all()
    return render_template('messages.html', received=received, sent=sent)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    sender_id = current_user.id
    receiver_id = data.get('receiver_id')
    subject = data.get('subject', '')
    message = data.get('message')

    if not message or not receiver_id:
        return jsonify({'error': 'Message and receiver_id are required'}), 400

    new_message = Message(sender_id=sender_id, receiver_id=receiver_id, subject=subject, message=message)
    db.session.add(new_message)
    db.session.commit()

    return jsonify({'message': 'Message sent successfully'}), 201

@app.route('/api/messages', methods=['GET'])
@login_required
def get_messages():
    messages = Message.query.filter_by(receiver_id=current_user.id).all()
    return jsonify([{
        'id': msg.id,
        'sender': msg.sender.name,
        'subject': msg.subject,
        'message': msg.message,
        'sent_at': msg.sent_at
    } for msg in messages]), 200

# Prescriptions API
@app.route('/api/prescriptions/<int:patient_id>', methods=['GET'])
@login_required
def get_prescriptions(patient_id):
    prescriptions = MedicalRecord.query.filter_by(patient_id=patient_id).all()
    return jsonify([{
        'doctor': record.doctor.name,
        'prescription': record.prescription,
        'visit_date': record.visit_date,
        'notes': record.visit_notes
    } for record in prescriptions]), 200

# Lab Records API
@app.route('/api/lab_records/<int:patient_id>', methods=['GET'])
@login_required
def get_lab_records(patient_id):
    lab_records = MedicalRecord.query.filter_by(patient_id=patient_id).all()
    return jsonify([{
        'test_name': record.lab_results,
        'visit_date': record.visit_date,
        'status': 'Completed' if record.lab_results else 'Pending'
    } for record in lab_records]), 200

# Patient Details API
@app.route('/api/patient_details/<int:patient_id>', methods=['GET'])
@login_required
def get_patient_details(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    user = patient.user

    return jsonify({
        'name': user.name,
        'age': (datetime.utcnow() - user.created_at).days // 365,
        'email': user.email,
        'phone': user.email,  # Assuming phone is stored in email for now
        'disease': patient.disease,
        'location': patient.assigned_hospital
    }), 200

@app.route('/update_patient/<int:patient_id>', methods=['POST'])
@login_required
def update_patient(patient_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()
    
    if 'assigned_hospital' in data:
        patient.assigned_hospital = data['assigned_hospital']
    if 'notice_period' in data:
        patient.notice_period = data['notice_period']
    if 'notes' in data:
        patient.patient_notes = data['notes']
        
    db.session.commit()
    return jsonify({'message': 'Patient updated successfully'})

@app.route('/reschedule_appointment', methods=['POST'])
@login_required
def reschedule_appointment():
    if current_user.role != 'patient':
        return jsonify({'error': 'Unauthorized'}), 403
        
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    new_date = datetime.strptime(request.form.get('new_date'), '%Y-%m-%d %H:%M')
    
    if (new_date - datetime.utcnow()).days < patient.notice_period:
        return jsonify({
            'error': f'Please provide at least {patient.notice_period} days notice for rescheduling'
        }), 400
        
    patient.next_visit = new_date
    db.session.commit()
    
    # Notify hospital staff
    notification = Notification(
        user_id=1,  # Admin will receive this
        title=f"Appointment Rescheduled - Patient {patient.id}",
        message=f"Patient {current_user.name} rescheduled their appointment to {new_date.strftime('%Y-%m-%d %H:%M')}",
        type='appointment',
        priority='normal'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'message': 'Appointment rescheduled successfully'})

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)

# Separate dashboards for each role
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role not in ['admin', 'hospital_admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    # Show hospital dashboard for hospital_admin
    if current_user.role == 'hospital_admin':
        hospital = Hospital.query.filter_by(email=current_user.email).first()
        hospitals = [hospital] if hospital else []
        patients = Patient.query.all()
        return render_template('hospitals.html', user=current_user, hospitals=hospitals, patients=patients)
    # Show admin dashboard for admin
    patients = Patient.query.all()
    return render_template('admin_dashboard.html', user=current_user, patients=patients)

@app.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    return render_template('patient_dashboard.html', user=current_user, patient=patient)

@app.route('/ngo_dashboard')
@login_required
def ngo_dashboard():
    if current_user.role != 'ngo_admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    patients = Patient.query.all()
    disease_counts = {d: 0 for d in ['Cancer', 'TB', 'AIDS', 'HIV']}
    for p in patients:
        if p.disease in disease_counts:
            disease_counts[p.disease] += 1
    ngo = {
        'name': 'Hope & Health Network',
        'pincode': '560040',
        'email': 'ngo@gmail.com',
        'address': '#23, 4th Cross, Vijayanagar, Bangalore, Karnataka - 560040',
        'symbol': 'https://img.icons8.com/color/96/000000/charity.png',
        'badge': 'NGO'
    }
    return render_template('ngo_dashboard.html', user=current_user, patients=patients, disease_counts=disease_counts, ngo=ngo)

@app.route('/appointments')
@login_required
def appointments():
    if current_user.role != 'patient':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    # You can expand this to show real appointments
    return render_template('appointments.html', user=current_user)

@app.route('/medical_records')
@login_required
def medical_records():
    if current_user.role != 'patient':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    # You can expand this to show real medical records
    return render_template('medical_records.html', user=current_user)

@app.route('/hospitals')
@login_required
def hospitals():
    if current_user.role not in ['admin', 'hospital']:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    if current_user.role == 'hospital':
        # Show only this hospital's data
        hospital = Hospital.query.filter_by(email=current_user.email).first()
        hospitals = [hospital] if hospital else []
    else:
        hospitals = Hospital.query.all()
    patients = Patient.query.all()
    return render_template('hospitals.html', user=current_user, hospitals=hospitals, patients=patients)

@app.route('/hospitals_dashboard')
@login_required
def hospitals_dashboard():
    if current_user.role != 'hospital':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    hospitals = Hospital.query.all()
    patients = Patient.query.all()
    # You may want to fetch appointments and next visits here as well
    # Example: appointments = Appointment.query.all()
    return render_template('hospitals.html', user=current_user, hospitals=hospitals, patients=patients)

@app.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    if current_user.role not in ['admin', 'hospital_staff']:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Placeholder: handle patient creation
        flash('Patient added (demo only).', 'success')
        return redirect(url_for('hospitals'))
    return render_template('add_patient.html', user=current_user)

@app.route('/hospital_dashboard')
@login_required
def hospital_dashboard():
    if current_user.role != 'hospital_admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    # Predefined hospitals
    hospitals = [
        {'id': 1, 'name': 'SDM Hospital', 'area': 'Dharwad', 'pincode': '580001', 'address': 'SDM Hospital, Sattur Colony, Dharwad, Karnataka'},
        {'id': 2, 'name': 'KIMS Hospital', 'area': 'Hubli', 'pincode': '580022', 'address': 'KIMS Hospital, Vidyanagar, Hubli, Karnataka'},
        {'id': 3, 'name': 'Balaji Hospital', 'area': 'Hubli', 'pincode': '580021', 'address': 'Balaji Hospital, Gokul Road, Hubli, Karnataka'},
        {'id': 4, 'name': 'Civil Hospital', 'area': 'Dharwad', 'pincode': '580002', 'address': 'Civil Hospital, Malmaddi, Dharwad, Karnataka'}
    ]

    # Fixed NGO staff per hospital
    hospital_staff = {
        1: [ # SDM
            {'id': 1, 'name': 'Ravi', 'area': 'Hubli City', 'img': 'https://randomuser.me/api/portraits/men/11.jpg'},
            {'id': 2, 'name': 'Sneha', 'area': 'Dharwad', 'img': 'https://randomuser.me/api/portraits/women/21.jpg'}
        ],
        2: [ # KIMS
            {'id': 3, 'name': 'Arjun', 'area': 'Gokul Road', 'img': 'https://randomuser.me/api/portraits/men/22.jpg'},
            {'id': 4, 'name': 'Priya', 'area': 'Vidyanagar', 'img': 'https://randomuser.me/api/portraits/women/23.jpg'}
        ],
        3: [ # Balaji
            {'id': 5, 'name': 'Rahul', 'area': 'Hubli', 'img': 'https://randomuser.me/api/portraits/men/24.jpg'},
            {'id': 6, 'name': 'Pooja', 'area': 'Hubli', 'img': 'https://randomuser.me/api/portraits/women/24.jpg'}
        ],
        4: [ # Civil
            {'id': 7, 'name': 'Mahesh', 'area': 'Dharwad', 'img': 'https://randomuser.me/api/portraits/men/25.jpg'},
            {'id': 8, 'name': 'Kavya', 'area': 'Dharwad', 'img': 'https://randomuser.me/api/portraits/women/25.jpg'}
        ]
    }

    # Fixed patients per staff (demo, use real DB in prod)
    staff_patients = {
        1: [ # Ravi
            {'id': 1, 'name': 'Anita', 'last_visit': '2026-04-10', 'next_visit': '2026-05-01', 'disease': 'Diabetes', 'medicines': ['Insulin', 'Metformin']},
            {'id': 2, 'name': 'Kiran', 'last_visit': '2026-03-22', 'next_visit': '2026-04-25', 'disease': 'BP', 'medicines': ['Amlodipine']}
        ],
        2: [ # Sneha
            {'id': 3, 'name': 'Meena', 'last_visit': '2026-04-01', 'next_visit': '2026-04-30', 'disease': 'AIDS', 'medicines': ['Iron', 'Calcium']}
        ],
        3: [ # Arjun
            {'id': 4, 'name': 'Ramesh', 'last_visit': '2026-03-15', 'next_visit': '2026-04-20', 'disease': 'Cancer', 'medicines': ['Imatinib']}
        ],
        4: [ # Priya
            {'id': 5, 'name': 'Sunita', 'last_visit': '2026-03-10', 'next_visit': '2026-04-18', 'disease': 'TB', 'medicines': ['Rifampicin']}
        ],
        5: [ # Rahul
            {'id': 6, 'name': 'Ajay', 'last_visit': '2026-03-05', 'next_visit': '2026-04-15', 'disease': 'Asthma', 'medicines': ['Salbutamol']}
        ],
        6: [ # Pooja
            {'id': 7, 'name': 'Neha', 'last_visit': '2026-03-01', 'next_visit': '2026-04-10', 'disease': 'Pregnancy care', 'medicines': ['Folic Acid']}
        ],
        7: [ # Mahesh
            {'id': 8, 'name': 'Deepak', 'last_visit': '2026-02-25', 'next_visit': '2026-04-05', 'disease': 'Diabetes', 'medicines': ['Insulin']}
        ],
        8: [ # Kavya
            {'id': 9, 'name': 'Lata', 'last_visit': '2026-02-20', 'next_visit': '2026-04-02', 'disease': 'BP', 'medicines': ['Amlodipine']}
        ]
    }

    # Compose hospital_staff_patients for template
    hospital_staff_patients = {}
    for h in hospitals:
        staff_list = []
        for staff in hospital_staff[h['id']]:
            s = staff.copy()
            s['patients'] = staff_patients.get(staff['id'], [])
            staff_list.append(s)
        hospital_staff_patients[h['id']] = staff_list

    return render_template('hospitals.html', user=current_user, hospitals=hospitals, hospital_staff_patients=hospital_staff_patients)

@app.route('/update_next_visit', methods=['POST'])
@login_required
def update_next_visit():
    if current_user.role != 'hospital_admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    patient_id = data.get('patient_id')
    new_date = data.get('next_visit')
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    # Prevent duplicate next visit date
    if patient.next_visit and patient.next_visit.strftime('%Y-%m-%d') == new_date:
        return jsonify({'error': 'This date is already set as the next visit.'}), 400
    # Update next visit
    patient.next_visit = datetime.strptime(new_date, '%Y-%m-%d')
    db.session.commit()
    # Send notification (in-app, extend for email/SMS if needed)
    notification = Notification(
        user_id=patient.user_id,
        title='Next Visit Updated',
        message=f'Your next visit is scheduled for {new_date}.',
        type='next_visit',
        priority='normal'
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Next visit updated and patient notified!'})

# ===== PRESCRIPTION ROUTES =====
@app.route('/prescriptions')
@login_required
def prescriptions():
    """View all prescriptions for current patient"""
    if current_user.role != 'patient':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient record not found.', 'danger')
        return redirect(url_for('patient_dashboard'))
    
    # Get prescriptions ordered by date (latest first)
    prescriptions = Prescription.query.filter_by(patient_id=patient.id).order_by(Prescription.prescription_date.desc()).all()
    
    return render_template('prescriptions.html', user=current_user, patient=patient, prescriptions=prescriptions)

@app.route('/prescription/<int:prescription_id>')
@login_required
def view_prescription(prescription_id):
    """View detailed prescription"""
    prescription = Prescription.query.get_or_404(prescription_id)
    
    # Security: only patient or assigned doctor can view
    patient = Patient.query.get(prescription.patient_id)
    if current_user.role == 'patient':
        if patient.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('login'))
    elif current_user.role == 'hospital_admin':
        if prescription.doctor_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    
    return render_template('prescription_detail.html', prescription=prescription, patient=patient)

@app.route('/prescription/add', methods=['GET', 'POST'])
@login_required
def add_prescription():
    """Add new prescription (Hospital staff only)"""
    if current_user.role != 'hospital_admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            patient_id = request.form.get('patient_id')
            patient = Patient.query.get_or_404(patient_id)
            
            # Parse medicines from form
            medicines_data = []
            medicine_names = request.form.getlist('medicine_name[]')
            medicine_dosages = request.form.getlist('medicine_dosage[]')
            medicine_frequencies = request.form.getlist('medicine_frequency[]')
            medicine_durations = request.form.getlist('medicine_duration[]')
            medicine_instructions = request.form.getlist('medicine_instructions[]')
            
            for i in range(len(medicine_names)):
                if medicine_names[i]:
                    medicines_data.append({
                        'medicine_name': medicine_names[i],
                        'dosage': medicine_dosages[i],
                        'frequency': medicine_frequencies[i],
                        'duration': medicine_durations[i],
                        'instructions': medicine_instructions[i]
                    })
            
            prescription = Prescription(
                patient_id=patient_id,
                doctor_id=current_user.id,
                doctor_name=current_user.name,
                medical_license=request.form.get('medical_license', ''),
                hospital_name=request.form.get('hospital_name', ''),
                hospital_address=request.form.get('hospital_address', ''),
                doctor_email=current_user.email,
                doctor_phone=request.form.get('doctor_phone', ''),
                patient_name=patient.user.name,
                patient_dob=patient.user.created_at,
                patient_gender=request.form.get('patient_gender', ''),
                patient_address=request.form.get('patient_address', ''),
                patient_email=patient.user.email,
                patient_phone=request.form.get('patient_phone', ''),
                insurance_details=request.form.get('insurance_details', ''),
                medicines=medicines_data,
                remarks=request.form.get('remarks', ''),
                prescription_date=datetime.utcnow()
            )
            
            db.session.add(prescription)
            db.session.commit()
            
            flash('Prescription added successfully!', 'success')
            return redirect(url_for('prescriptions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding prescription: {str(e)}', 'danger')
            return redirect(url_for('add_prescription'))
    
    # Get list of patients
    patients = Patient.query.all()
    return render_template('add_prescription.html', patients=patients, doctor=current_user)

@app.route('/api/prescriptions/<int:patient_id>')
@login_required
def api_get_prescriptions(patient_id):
    """API endpoint to get prescriptions for a patient"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Security check
    if current_user.role == 'patient' and patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).order_by(Prescription.prescription_date.desc()).all()
    
    return jsonify([{
        'id': p.id,
        'doctor_name': p.doctor_name,
        'prescription_date': p.prescription_date.strftime('%Y-%m-%d'),
        'medicines_count': len(p.medicines) if p.medicines else 0,
        'is_active': p.is_active
    } for p in prescriptions])

# ===== LAB RECORDS ROUTES =====
@app.route('/lab_records')
@login_required
def lab_records():
    """View all lab records for current patient"""
    if current_user.role != 'patient':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient record not found.', 'danger')
        return redirect(url_for('patient_dashboard'))
    
    # Get lab records ordered by date (latest first)
    records = LabRecord.query.filter_by(patient_id=patient.id).order_by(LabRecord.test_date.desc()).all()
    
    return render_template('lab_records.html', user=current_user, patient=patient, records=records)

@app.route('/lab_record/<int:record_id>')
@login_required
def view_lab_record(record_id):
    """View detailed lab record"""
    record = LabRecord.query.get_or_404(record_id)
    
    # Security: only patient or assigned doctor can view
    patient = Patient.query.get(record.patient_id)
    if current_user.role == 'patient':
        if patient.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('login'))
    elif current_user.role == 'hospital_admin':
        if record.doctor_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    
    return render_template('lab_record_detail.html', record=record, patient=patient)

@app.route('/lab_record/add', methods=['GET', 'POST'])
@login_required
def add_lab_record():
    """Add new lab record (Hospital staff only)"""
    if current_user.role != 'hospital_admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            patient_id = request.form.get('patient_id')
            patient = Patient.query.get_or_404(patient_id)
            
            # Parse test results from form
            results_data = []
            result_parameters = request.form.getlist('result_parameter[]')
            result_values = request.form.getlist('result_value[]')
            result_units = request.form.getlist('result_unit[]')
            result_normal_ranges = request.form.getlist('result_normal_range[]')
            result_statuses = request.form.getlist('result_status[]')
            
            for i in range(len(result_parameters)):
                if result_parameters[i]:
                    results_data.append({
                        'parameter': result_parameters[i],
                        'value': result_values[i],
                        'unit': result_units[i],
                        'normal_range': result_normal_ranges[i],
                        'status': result_statuses[i]
                    })
            
            record = LabRecord(
                patient_id=patient_id,
                doctor_id=current_user.id,
                test_name=request.form.get('test_name', ''),
                hospital_name=request.form.get('hospital_name', ''),
                hospital_location=request.form.get('hospital_location', ''),
                results=results_data,
                overall_status=request.form.get('overall_status', 'Pending'),
                notes=request.form.get('notes', ''),
                test_date=datetime.utcnow(),
                is_completed=request.form.get('is_completed', False)
            )
            
            db.session.add(record)
            db.session.commit()
            
            flash('Lab record added successfully!', 'success')
            return redirect(url_for('lab_records'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding lab record: {str(e)}', 'danger')
            return redirect(url_for('add_lab_record'))
    
    # Get list of patients
    patients = Patient.query.all()
    return render_template('add_lab_record.html', patients=patients, doctor=current_user)

@app.route('/api/lab_records/<int:patient_id>')
@login_required
def api_get_lab_records(patient_id):
    """API endpoint to get lab records for a patient"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Security check
    if current_user.role == 'patient' and patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    records = LabRecord.query.filter_by(patient_id=patient_id).order_by(LabRecord.test_date.desc()).all()
    
    return jsonify([{
        'id': r.id,
        'test_name': r.test_name,
        'test_date': r.test_date.strftime('%Y-%m-%d'),
        'hospital_name': r.hospital_name,
        'overall_status': r.overall_status,
        'is_completed': r.is_completed
    } for r in records])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
