#!/usr/bin/env python
"""
Quick Setup Guide for Prescription & Lab Records Feature
Run this to initialize and test the new features
"""

import os
import sys

def run_setup():
    print("\n" + "="*70)
    print("PRESCRIPTION & LAB RECORDS FEATURE - QUICK SETUP")
    print("="*70 + "\n")
    
    print("Step 1: Create Database Tables")
    print("-" * 70)
    print("Run the following commands to create the new tables:\n")
    
    print("Option A - Using Flask Migration:")
    print("  $ flask db migrate -m 'Add Prescription and LabRecord models'")
    print("  $ flask db upgrade\n")
    
    print("Option B - Using Direct Database Creation:")
    print("  $ flask shell")
    print("  >>> from app import app, db")
    print("  >>> with app.app_context():")
    print("  ...     db.create_all()")
    print("  >>> exit()\n")
    
    print("Step 2: Load Sample Data (Optional)")
    print("-" * 70)
    print("To test the features with sample data:\n")
    print("  $ flask shell")
    print("  >>> exec(open('sample_data.py').read())")
    print("  >>> exit()\n")
    
    print("Step 3: Start the Application")
    print("-" * 70)
    print("  $ python app.py\n")
    
    print("Step 4: Access the Features")
    print("-" * 70)
    print("\nFor PATIENTS:")
    print("  1. Login as patient (patient@gmail.com / patient123)")
    print("  2. Go to Patient Dashboard")
    print("  3. Click 'View My Prescriptions' or 'View My Lab Records'")
    print("  4. Click on any prescription/record to view full details")
    print("  5. Use Print button to print documents\n")
    
    print("For DOCTORS/HOSPITAL STAFF:")
    print("  1. Login as hospital admin")
    print("  2. Go to Hospital Dashboard")
    print("  3. Click 'Add Prescription' or 'Add Lab Record' buttons")
    print("  4. Select patient and fill in details")
    print("  5. Save and the patient will see it in their dashboard\n")
    
    print("="*70)
    print("KEY FEATURES")
    print("="*70 + "\n")
    
    print("📋 PRESCRIPTIONS:")
    print("  ✓ Add multiple medicines with dosage, frequency, duration")
    print("  ✓ Store doctor and hospital information")
    print("  ✓ Add remarks and precautions")
    print("  ✓ View prescription history")
    print("  ✓ Print prescriptions in professional format\n")
    
    print("🧪 LAB RECORDS:")
    print("  ✓ Add multiple test parameters with values")
    print("  ✓ Track test status (Normal/Abnormal/Pending/Completed)")
    print("  ✓ Store normal ranges and reference values")
    print("  ✓ View lab test history")
    print("  ✓ Generate detailed test reports\n")
    
    print("="*70)
    print("FILES MODIFIED/CREATED")
    print("="*70 + "\n")
    
    files_info = {
        "Modified": [
            "models.py - Added Prescription and LabRecord models",
            "app.py - Added routes for prescriptions and lab records",
            "templates/patient_dashboard.html - Added buttons to view prescriptions/lab records",
            "templates/hospital_dashboard.html - Added action buttons for doctors"
        ],
        "Created": [
            "templates/prescriptions.html - List prescriptions",
            "templates/prescription_detail.html - Prescription details/print",
            "templates/add_prescription.html - Add new prescription",
            "templates/lab_records.html - List lab records",
            "templates/lab_record_detail.html - Lab record details/print",
            "templates/add_lab_record.html - Add new lab record",
            "sample_data.py - Sample test data",
            "PRESCRIPTION_LAB_IMPLEMENTATION.md - Complete documentation"
        ]
    }
    
    for category, files in files_info.items():
        print(f"{category}:")
        for file in files:
            print(f"  • {file}")
        print()
    
    print("="*70)
    print("API ENDPOINTS")
    print("="*70 + "\n")
    
    endpoints = {
        "Patient": [
            "GET /prescriptions - View all prescriptions",
            "GET /prescription/<id> - View prescription details",
            "GET /lab_records - View all lab records",
            "GET /lab_record/<id> - View lab record details"
        ],
        "Doctor/Staff": [
            "GET /prescription/add - Add prescription form",
            "POST /prescription/add - Save prescription",
            "GET /lab_record/add - Add lab record form",
            "POST /lab_record/add - Save lab record"
        ],
        "API": [
            "GET /api/prescriptions/<patient_id> - Get prescriptions JSON",
            "GET /api/lab_records/<patient_id> - Get lab records JSON"
        ]
    }
    
    for category, routes in endpoints.items():
        print(f"{category}:")
        for route in routes:
            print(f"  • {route}")
        print()
    
    print("="*70)
    print("TROUBLESHOOTING")
    print("="*70 + "\n")
    
    troubleshoot = {
        "Database errors": [
            "Ensure MySQL is running",
            "Check database credentials in config.py",
            "Run: flask db upgrade"
        ],
        "Templates not found": [
            "Verify all template files are in templates/ directory",
            "Check file names are spelled correctly",
            "Ensure templates/base.html exists"
        ],
        "Import errors": [
            "Run: pip install -r requirements.txt",
            "Check that models.py has Prescription and LabRecord classes",
            "Verify app.py imports are updated"
        ],
        "Access denied": [
            "Verify user role is set correctly",
            "Check authentication is working",
            "Ensure current_user is logged in"
        ]
    }
    
    for issue, solutions in troubleshoot.items():
        print(f"❌ {issue}:")
        for solution in solutions:
            print(f"   ✓ {solution}")
        print()
    
    print("="*70)
    print("DATABASE SCHEMA")
    print("="*70 + "\n")
    
    print("Prescription Table:")
    print("  - id, patient_id, doctor_id")
    print("  - doctor_name, medical_license, hospital_name, hospital_address")
    print("  - doctor_email, doctor_phone")
    print("  - patient_name, patient_dob, patient_gender, patient_address")
    print("  - patient_email, patient_phone, insurance_details")
    print("  - medicines (JSON), remarks, prescription_date")
    print("  - created_at, updated_at, is_active\n")
    
    print("LabRecord Table:")
    print("  - id, patient_id, doctor_id")
    print("  - test_name, test_date")
    print("  - hospital_name, hospital_location")
    print("  - results (JSON), overall_status")
    print("  - notes, is_completed")
    print("  - created_at, updated_at\n")
    
    print("="*70)
    print("SUPPORT & DOCUMENTATION")
    print("="*70 + "\n")
    
    print("For detailed documentation, see:")
    print("  • PRESCRIPTION_LAB_IMPLEMENTATION.md - Full feature guide")
    print("  • sample_data.py - Sample data structure")
    print("  • This file (QUICK_START.md)\n")
    
    print("="*70)
    print("Ready to go! Start with Step 1 above.")
    print("="*70 + "\n")

if __name__ == '__main__':
    run_setup()
