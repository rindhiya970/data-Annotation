#!/usr/bin/env python3
"""
Diagnostic script to check backend setup.
Run this to identify issues before starting the server.

Usage:
    python check_setup.py
"""

import sys

def check_imports():
    """Check if all required packages are installed."""
    print("=" * 60)
    print("1. Checking Python Packages")
    print("=" * 60)
    
    required_packages = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('flask_jwt_extended', 'Flask-JWT-Extended'),
        ('flask_cors', 'Flask-CORS'),
        ('pymysql', 'PyMySQL'),
        ('werkzeug', 'Werkzeug'),
        ('cv2', 'opencv-python')
    ]
    
    missing = []
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - NOT INSTALLED")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print("pip install flask flask-sqlalchemy flask-jwt-extended flask-cors pymysql opencv-python")
        return False
    
    print("\n✅ All required packages installed!")
    return True

def check_database_connection():
    """Check if database connection works."""
    print("\n" + "=" * 60)
    print("2. Checking Database Connection")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.extensions import db
        
        app = create_app()
        
        with app.app_context():
            # Try to connect
            db.engine.connect()
            print(f"✅ Database connection successful!")
            print(f"   URL: {db.engine.url}")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed!")
        print(f"   Error: {str(e)}")
        print("\n💡 Solutions:")
        print("   1. Make sure MySQL is running")
        print("   2. Create database: CREATE DATABASE annotation_db;")
        print("   3. Check credentials in app/config.py")
        return False

def check_database_tables():
    """Check if database tables exist."""
    print("\n" + "=" * 60)
    print("3. Checking Database Tables")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.extensions import db
        
        app = create_app()
        
        with app.app_context():
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['users', 'files', 'videos', 'frames', 'annotations']
            
            if not tables:
                print("❌ No tables found in database!")
                print("\n💡 Solution: Run 'python init_db.py' to create tables")
                return False
            
            print(f"Found tables: {tables}")
            
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                print(f"\n⚠️  Missing tables: {missing_tables}")
                print("\n💡 Solution: Run 'python init_db.py' to create missing tables")
                return False
            
            print("\n✅ All required tables exist!")
            return True
            
    except Exception as e:
        print(f"❌ Could not check tables!")
        print(f"   Error: {str(e)}")
        return False

def check_config():
    """Check configuration."""
    print("\n" + "=" * 60)
    print("4. Checking Configuration")
    print("=" * 60)
    
    try:
        from app import create_app
        
        app = create_app()
        
        print(f"✅ SECRET_KEY: {'*' * 20}")
        print(f"✅ JWT_SECRET_KEY: {'*' * 20}")
        print(f"✅ SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"✅ UPLOAD_FOLDER: {app.config['UPLOAD_FOLDER']}")
        print(f"✅ MAX_CONTENT_LENGTH: {app.config['MAX_CONTENT_LENGTH']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error!")
        print(f"   Error: {str(e)}")
        return False

def check_models():
    """Check if models can be imported."""
    print("\n" + "=" * 60)
    print("5. Checking Models")
    print("=" * 60)
    
    models = [
        ('app.models.user', 'User'),
        ('app.models.file', 'File'),
        ('app.models.video', 'Video'),
        ('app.models.frame', 'Frame'),
        ('app.models.annotation', 'Annotation')
    ]
    
    for module, name in models:
        try:
            __import__(module)
            print(f"✅ {name} model")
        except Exception as e:
            print(f"❌ {name} model - Error: {str(e)}")
            return False
    
    print("\n✅ All models imported successfully!")
    return True

def main():
    """Run all checks."""
    print("\n" + "=" * 60)
    print("🔍 Backend Setup Diagnostic")
    print("=" * 60)
    
    checks = [
        check_imports(),
        check_config(),
        check_models(),
        check_database_connection(),
        check_database_tables()
    ]
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if all(checks):
        print("\n✅ All checks passed! Your backend is ready to run.")
        print("\nStart the server with:")
        print("  python run.py")
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Install missing packages: pip install -r requirements.txt")
        print("  2. Create database: mysql -u root -p -e 'CREATE DATABASE annotation_db;'")
        print("  3. Initialize tables: python init_db.py")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
