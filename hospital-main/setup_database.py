"""
Database Migration Helper for Prescription & Lab Records Feature

This script helps you set up the database for the new features.

Usage:
    1. Using Flask-Migrate (Recommended):
       $ flask db migrate -m "Add Prescription and LabRecord models"
       $ flask db upgrade
    
    2. Using Direct Database Creation:
       $ python
       >>> from setup_database import setup_database
       >>> setup_database()
    
    3. Or run this script directly:
       $ python setup_database.py
"""

from app import app, db
from models import Prescription, LabRecord

def setup_database():
    """Setup database tables for prescriptions and lab records"""
    
    print("\n" + "="*70)
    print("DATABASE SETUP FOR PRESCRIPTION & LAB RECORDS")
    print("="*70 + "\n")
    
    try:
        with app.app_context():
            print("Step 1: Creating tables...")
            
            # Create all tables
            db.create_all()
            
            print("✓ Tables created successfully\n")
            
            print("Step 2: Verifying tables...")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['prescription', 'lab_record']
            for table in required_tables:
                if table in tables:
                    print(f"✓ Table '{table}' exists")
                else:
                    print(f"✗ Table '{table}' NOT FOUND - Setup may have failed")
                    return False
            
            print("\nStep 3: Verifying columns...")
            
            # Verify Prescription table columns
            print("\nPrescription Table Columns:")
            prescription_cols = inspector.get_columns('prescription')
            for col in prescription_cols:
                print(f"  ✓ {col['name']} ({col['type']})")
            
            # Verify LabRecord table columns
            print("\nLabRecord Table Columns:")
            lab_cols = inspector.get_columns('lab_record')
            for col in lab_cols:
                print(f"  ✓ {col['name']} ({col['type']})")
            
            print("\n" + "="*70)
            print("✓ DATABASE SETUP COMPLETE")
            print("="*70)
            print("\nYou can now:")
            print("  1. Load sample data: python -c \"exec(open('sample_data.py').read())\"")
            print("  2. Start the application: python app.py")
            print("  3. Login and test the features")
            
            return True
            
    except Exception as e:
        print(f"\n✗ ERROR during database setup: {str(e)}")
        print("\nTroubleshooting tips:")
        print("  1. Ensure MySQL is running")
        print("  2. Verify database credentials in config.py")
        print("  3. Check if base tables (user, patient) exist")
        print("  4. Try running: flask db upgrade")
        import traceback
        traceback.print_exc()
        return False

def verify_setup():
    """Verify that the database is properly set up"""
    
    print("\n" + "="*70)
    print("DATABASE VERIFICATION")
    print("="*70 + "\n")
    
    try:
        with app.app_context():
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("Required tables:")
            checks = {
                'user': 'User accounts',
                'patient': 'Patient records',
                'prescription': 'Prescriptions',
                'lab_record': 'Lab records'
            }
            
            all_good = True
            for table, description in checks.items():
                if table in tables:
                    print(f"✓ {table:15} - {description}")
                else:
                    print(f"✗ {table:15} - {description} [MISSING]")
                    all_good = False
            
            if all_good:
                print("\n" + "="*70)
                print("✓ ALL TABLES PRESENT - DATABASE IS READY")
                print("="*70)
            else:
                print("\n" + "="*70)
                print("✗ SOME TABLES ARE MISSING - Run setup first")
                print("="*70)
            
            return all_good
            
    except Exception as e:
        print(f"\n✗ ERROR during verification: {str(e)}")
        return False

def reset_database():
    """Drop all tables and recreate them (DANGEROUS - Use with caution)"""
    
    print("\n" + "="*70)
    print("⚠️  DATABASE RESET (ALL DATA WILL BE DELETED)")
    print("="*70 + "\n")
    
    confirm = input("Type 'YES' to confirm database reset: ").strip()
    
    if confirm != 'YES':
        print("Reset cancelled.")
        return False
    
    try:
        with app.app_context():
            print("\nDropping all tables...")
            db.drop_all()
            print("✓ Tables dropped")
            
            print("Creating new tables...")
            db.create_all()
            print("✓ Tables created")
            
            print("\n" + "="*70)
            print("✓ DATABASE RESET COMPLETE")
            print("="*70)
            
            return True
            
    except Exception as e:
        print(f"\n✗ ERROR during reset: {str(e)}")
        return False

def main():
    """Main menu"""
    
    while True:
        print("\n" + "="*70)
        print("DATABASE SETUP MENU")
        print("="*70)
        print("\n1. Setup Database (Create tables)")
        print("2. Verify Database Setup")
        print("3. Load Sample Data")
        print("4. Reset Database (⚠️  DESTRUCTIVE)")
        print("5. Exit")
        print("\n" + "="*70)
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            setup_database()
        
        elif choice == '2':
            verify_setup()
        
        elif choice == '3':
            print("\nLoading sample data...")
            try:
                exec(open('sample_data.py').read())
            except Exception as e:
                print(f"Error loading sample data: {str(e)}")
        
        elif choice == '4':
            reset_database()
        
        elif choice == '5':
            print("\nGoodbye!")
            break
        
        else:
            print("\n✗ Invalid option. Please try again.")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'setup':
            setup_database()
        elif command == 'verify':
            verify_setup()
        elif command == 'reset':
            reset_database()
        else:
            print("Usage: python setup_database.py [setup|verify|reset]")
            print("\nOr run without arguments for interactive menu:")
            print("  python setup_database.py")
    else:
        main()
