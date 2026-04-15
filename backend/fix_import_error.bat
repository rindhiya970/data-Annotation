@echo off
echo ========================================
echo Fix Import Error - Clean Cache
echo ========================================
echo.

echo STEP 1: Stop Flask Server
echo ========================================
echo Press Ctrl+C in the Flask terminal window to stop the server
echo Then press Enter here to continue...
pause > nul
echo.

echo STEP 2: Deleting __pycache__ folders...
echo ========================================
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo Deleting: %%d
    rd /s /q "%%d"
)
echo Done!
echo.

echo STEP 3: Deleting .pyc files...
echo ========================================
del /s /q *.pyc 2>nul
echo Done!
echo.

echo STEP 4: Verifying file_service.py exists...
echo ========================================
if exist "app\services\file_service.py" (
    echo [OK] File exists: app\services\file_service.py
) else (
    echo [ERROR] File not found: app\services\file_service.py
    pause
    exit /b 1
)
echo.

echo STEP 5: Checking for duplicate files...
echo ========================================
dir /s /b file_service.py
echo.

echo STEP 6: Activating virtual environment...
echo ========================================
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

echo STEP 7: Testing import...
echo ========================================
python -c "from app.services.file_service import get_file_by_id, save_uploaded_file, get_user_files; print('[OK] All functions imported successfully')"
if errorlevel 1 (
    echo [ERROR] Import test failed!
    pause
    exit /b 1
)
echo.

echo ========================================
echo SUCCESS! All checks passed!
echo ========================================
echo.
echo You can now restart Flask server:
echo   python run.py
echo.
echo Or run full initialization:
echo   python init_db.py
echo   python run.py
echo.

pause
