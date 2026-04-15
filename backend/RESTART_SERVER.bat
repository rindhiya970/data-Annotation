@echo off
echo ========================================
echo   RESTARTING FLASK SERVER
echo ========================================
echo.
echo Stopping any running Flask processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *run.py*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting Flask server...
echo.
python run.py
