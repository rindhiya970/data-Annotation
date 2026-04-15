@echo off
echo ========================================
echo Restarting Flask Backend
echo ========================================
echo.
echo IMPORTANT: This will restart Flask with updated configuration
echo - MAX_CONTENT_LENGTH: 100MB (for video uploads)
echo - MAX_VIDEO_DURATION: 300 seconds (5 minutes)
echo.
echo Press Ctrl+C to stop Flask when needed
echo.
pause

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo Starting Flask backend...
echo.
python run.py

pause
