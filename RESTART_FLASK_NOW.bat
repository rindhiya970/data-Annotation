@echo off
echo ========================================
echo   RESTARTING FLASK SERVER
echo ========================================
echo.
echo Step 1: Killing ALL Python processes...
taskkill /F /IM python.exe /T 2>nul
if %errorlevel% == 0 (
    echo ✓ Python processes stopped
) else (
    echo ✓ No Python processes were running
)

echo.
echo Step 2: Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo Step 3: Starting Flask server...
cd backend
start "Flask Server - DO NOT CLOSE" cmd /k "python run.py"

echo.
echo Step 4: Waiting for server to start...
timeout /t 5 /nobreak >nul

echo.
echo Step 5: Testing annotation endpoint...
cd ..
python test_annotation_endpoint.py

echo.
echo ========================================
echo   DONE!
echo ========================================
echo.
echo Flask server is now running in a new window.
echo.
echo NEXT STEPS:
echo 1. Go to your browser
echo 2. Refresh the page (F5)
echo 3. Click on an image
echo 4. The annotation page should load!
echo.
pause
