"""
Sample Test Data for Prescription and Lab Records
Insert this sample data to test the features

Usage:
    python
    >>> from app import app, db
    >>> from models import Patient, Prescription, LabRecord, User
    >>> from datetime import datetime, timedelta
    >>> exec(open('sample_data.py').read())
    
Or run directly with Flask shell:
    flask shell
    >>> exec(open('sample_data.py').read())
"""

from app import app, db
from models import Patient, Prescription, LabRecord, User
from datetime import datetime, timedelta

def add_sample_data():
    with app.app_context():
        try:
            # Get first patient and user
            patient = Patient.query.first()
            user = User.query.filter_by(role='patient').first()
            doctor = User.query.filter_by(role='hospital_admin').first()
            
            if not patient or not user or not doctor:
                print("Error: Patient, User, or Doctor not found. Please create them first.")
                return
            
            print(f"Adding sample prescriptions for patient: {patient.user.name}")
            
            # Sample Prescription 1 - Latest
            prescription1 = Prescription(
                patient_id=patient.id,
                doctor_id=doctor.id,
                doctor_name=doctor.name,
                medical_license="ML/ML123456",
                hospital_name="Apollo Hospital",
                hospital_address="123 Medical Street, Bangalore, Karnataka 560040",
                doctor_email=doctor.email,
                doctor_phone="+91-9876543210",
                patient_name=patient.user.name,
                patient_dob=datetime(1990, 5, 15),
                patient_gender="Male",
                patient_address="456 Patient Lane, Bangalore, Karnataka",
                patient_email=patient.user.email,
                patient_phone="+91-9123456789",
                insurance_details="Aetna Policy #POL123456",
                medicines=[
                    {
                        'medicine_name': 'Paracetamol',
                        'dosage': '500mg',
                        'frequency': 'Twice daily',
                        'duration': '5 days',
                        'instructions': 'After food'
                    },
                    {
                        'medicine_name': 'Azithromycin',
                        'dosage': '250mg',
                        'frequency': 'Once daily',
                        'duration': '3 days',
                        'instructions': 'Morning before breakfast'
                    },
                    {
                        'medicine_name': 'Cough Syrup',
                        'dosage': '10ml',
                        'frequency': 'Three times daily',
                        'duration': '7 days',
                        'instructions': 'After meals'
                    }
                ],
                remarks='Avoid dairy products. Drink plenty of water. Rest well. If fever persists, contact immediately.',
                prescription_date=datetime.utcnow()
            )
            
            # Sample Prescription 2 - Older
            prescription2 = Prescription(
                patient_id=patient.id,
                doctor_id=doctor.id,
                doctor_name=doctor.name,
                medical_license="ML/ML123456",
                hospital_name="KIMS Hospital",
                hospital_address="456 Healthcare Ave, Hubli, Karnataka 580022",
                doctor_email=doctor.email,
                doctor_phone="+91-9876543210",
                patient_name=patient.user.name,
                patient_dob=datetime(1990, 5, 15),
                patient_gender="Male",
                patient_address="456 Patient Lane, Bangalore, Karnataka",
                patient_email=patient.user.email,
                patient_phone="+91-9123456789",
                insurance_details="ICICI Health Policy #POL654321",
                medicines=[
                    {
                        'medicine_name': 'Metformin',
                        'dosage': '500mg',
                        'frequency': 'Twice daily',
                        'duration': 'Ongoing',
                        'instructions': 'With meals'
                    },
                    {
                        'medicine_name': 'Atorvastatin',
                        'dosage': '10mg',
                        'frequency': 'Once daily',
                        'duration': 'Ongoing',
                        'instructions': 'At bedtime'
                    }
                ],
                remarks='Monitor blood sugar levels regularly. Avoid sugary foods. Regular exercise recommended.',
                prescription_date=datetime.utcnow() - timedelta(days=15)
            )
            
            db.session.add(prescription1)
            db.session.add(prescription2)
            db.session.commit()
            print(f"✓ Added {2} sample prescriptions")
            
            # Sample Lab Records
            print(f"Adding sample lab records for patient: {patient.user.name}")
            
            # Sample Lab Record 1 - Latest
            lab_record1 = LabRecord(
                patient_id=patient.id,
                doctor_id=doctor.id,
                test_name="Complete Blood Count (CBC)",
                hospital_name="Apollo Diagnostics",
                hospital_location="123 Medical Street, Bangalore",
                results=[
                    {
                        'parameter': 'Hemoglobin',
                        'value': '13.5',
                        'unit': 'g/dL',
                        'normal_range': '13.5-17.5',
                        'status': 'Normal'
                    },
                    {
                        'parameter': 'WBC Count',
                        'value': '7500',
                        'unit': 'cells/µL',
                        'normal_range': '4500-11000',
                        'status': 'Normal'
                    },
                    {
                        'parameter': 'Platelets',
                        'value': '250000',
                        'unit': 'cells/µL',
                        'normal_range': '150000-400000',
                        'status': 'Normal'
                    }
                ],
                overall_status='Normal',
                notes='All parameters within normal range. Patient is healthy.',
                test_date=datetime.utcnow(),
                is_completed=True
            )
            
            # Sample Lab Record 2 - Older with abnormal results
            lab_record2 = LabRecord(
                patient_id=patient.id,
                doctor_id=doctor.id,
                test_name="Fasting Blood Sugar (FBS) Test",
                hospital_name="KIMS Diagnostics",
                hospital_location="456 Healthcare Ave, Hubli",
                results=[
                    {
                        'parameter': 'Fasting Sugar',
                        'value': '125',
                        'unit': 'mg/dL',
                        'normal_range': '70-100',
                        'status': 'Abnormal'
                    },
                    {
                        'parameter': 'HbA1c',
                        'value': '6.8',
                        'unit': '%',
                        'normal_range': '<5.7',
                        'status': 'Abnormal'
                    }
                ],
                overall_status='Abnormal',
                notes='Elevated fasting blood sugar. Recommend dietary changes and lifestyle modifications.',
                test_date=datetime.utcnow() - timedelta(days=10),
                is_completed=True
            )
            
            # Sample Lab Record 3 - Pending
            lab_record3 = LabRecord(
                patient_id=patient.id,
                doctor_id=doctor.id,
                test_name="Lipid Profile",
                hospital_name="Apollo Diagnostics",
                hospital_location="123 Medical Street, Bangalore",
                results=[],
                overall_status='Pending',
                notes='Test scheduled. Results will be available within 24 hours.',
                test_date=datetime.utcnow() + timedelta(hours=2),
                is_completed=False
            )
            
            db.session.add(lab_record1)
            db.session.add(lab_record2)
            db.session.add(lab_record3)
            db.session.commit()
            print(f"✓ Added {3} sample lab records")
            
            print("\n" + "="*50)
            print("Sample data added successfully!")
            print("="*50)
            print(f"\nPatient: {patient.user.name}")
            print(f"Email: {patient.user.email}")
            print(f"\nPrescriptions added: 2")
            print(f"Lab Records added: 3")
            print("\nYou can now:")
            print("1. Login as patient to view prescriptions and lab records")
            print("2. Login as doctor to add more prescriptions/lab records")
            print("\nTest credentials:")
            print("- Patient email: patient@gmail.com, password: patient123")
            print("- Doctor email: (hospital admin), password: (your password)")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding sample data: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_sample_data()
