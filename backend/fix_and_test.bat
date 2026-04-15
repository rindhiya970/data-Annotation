@echo off
echo ========================================
echo File Upload Fix Script
echo ========================================
echo.

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

echo Step 2: Initializing database...
python init_db.py
if errorlevel 1 (
    echo ERROR: Database initialization failed
    pause
    exit /b 1
)
echo Database initialized successfully!
echo.

echo Step 3: Starting Flask server...
echo Server will start on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python run.py

pause
