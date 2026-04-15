@echo off
echo ========================================
echo FLASK FILE UPLOAD FIX
echo ========================================
echo.

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate venv
    echo Make sure venv exists in backend folder
    pause
    exit /b 1
)
echo ✅ Virtual environment activated
echo.

echo Step 2: Initializing database...
python init_db.py
if errorlevel 1 (
    echo ERROR: Database initialization failed
    pause
    exit /b 1
)
echo ✅ Database initialized
echo.

echo Step 3: Starting Flask server...
echo Server will start on http://localhost:5000
echo.
echo ⚠️  Keep this window open!
echo ⚠️  Test upload from Vue frontend at http://localhost:5173/media/upload
echo.
echo Press Ctrl+C to stop the server
echo.
python run.py

pause
