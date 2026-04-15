#!/usr/bin/env python3
"""
Quick verification script to check if the Flask backend is properly configured.
Run this before starting the server to catch configuration issues early.
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists."""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {dirpath}")
        return False

def check_env_file():
    """Check frontend .env file."""
    env_path = os.path.join('frontend', '.env')
    if not os.path.exists(env_path):
        print(f"❌ Frontend .env file NOT FOUND: {env_path}")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    if 'VITE_API_BASE_URL=http://127.0.0.1:5000/api' in content:
        print(f"✅ Frontend .env configured correctly")
        return True
    else:
        print(f"❌ Frontend .env missing /api prefix")
        print(f"   Expected: VITE_API_BASE_URL=http://127.0.0.1:5000/api")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Flask + Vue Setup Verification")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Check backend structure
    print("📁 Backend Structure:")
    all_checks_passed &= check_file_exists('backend/run.py', 'Backend entry point')
    all_checks_passed &= check_file_exists('backend/app/__init__.py', 'App factory')
    all_checks_passed &= check_file_exists('backend/app/config.py', 'Config file')
    all_checks_passed &= check_directory_exists('backend/app/routes', 'Routes directory')
    all_checks_passed &= check_directory_exists('backend/app/services', 'Services directory')
    all_checks_passed &= check_directory_exists('backend/app/models', 'Models directory')
    print()
    
    # Check frontend structure
    print("📁 Frontend Structure:")
    all_checks_passed &= check_file_exists('frontend/package.json', 'Package.json')
    all_checks_passed &= check_file_exists('frontend/vite.config.js', 'Vite config')
    all_checks_passed &= check_file_exists('frontend/src/main.js', 'Main.js')
    all_checks_passed &= check_directory_exists('frontend/src/services', 'Services directory')
    all_checks_passed &= check_directory_exists('frontend/src/stores', 'Stores directory')
    print()
    
    # Check configuration files
    print("⚙️  Configuration:")
    all_checks_passed &= check_env_file()
    all_checks_passed &= check_file_exists('frontend/src/api/axios.js', 'Axios instance')
    all_checks_passed &= check_file_exists('frontend/src/config/api.js', 'API config')
    print()
    
    # Check critical service files
    print("🔧 Service Files:")
    all_checks_passed &= check_file_exists('frontend/src/services/authService.js', 'Auth service')
    all_checks_passed &= check_file_exists('frontend/src/stores/authStore.js', 'Auth store')
    all_checks_passed &= check_file_exists('backend/app/routes/auth_routes.py', 'Auth routes')
    all_checks_passed &= check_file_exists('backend/app/routes/file_routes.py', 'File routes')
    print()
    
    # Check uploads directory
    print("📂 Upload Directory:")
    upload_dir = os.path.join('backend', 'app', 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
        print(f"✅ Created upload directory: {upload_dir}")
    else:
        print(f"✅ Upload directory exists: {upload_dir}")
    print()
    
    # Check database
    print("💾 Database:")
    db_path = os.path.join('backend', 'app', 'app.db')
    if os.path.exists(db_path):
        print(f"✅ Database exists: {db_path}")
    else:
        print(f"⚠️  Database not found: {db_path}")
        print(f"   Run: cd backend && python init_db.py")
    print()
    
    # Final summary
    print("=" * 60)
    if all_checks_passed:
        print("✅ All checks passed! Your setup is ready.")
        print()
        print("Next steps:")
        print("1. Start backend:  cd backend && python run.py")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Open browser:   http://localhost:5173/login")
        print("4. Login with:     test@example.com / password123")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
