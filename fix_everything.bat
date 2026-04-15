@echo off
echo ========================================
echo   FIXING ANNOTATION SYSTEM
echo ========================================
echo.
echo This will:
echo 1. Stop Flask server
echo 2. Restart Flask server
echo 3. Test the endpoints
echo.
pause

echo.
echo [1/3] Stopping Flask server...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/3] Starting Flask server...
cd backend
start "Flask Server" python run.py
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Testing endpoints...
cd ..
python test_annotation_endpoint.py

echo.
echo ========================================
echo   NEXT STEPS:
echo ========================================
echo.
echo 1. Go to your browser
echo 2. Press F12 (open DevTools)
echo 3. Go to Application tab
echo 4. Click "Clear site data"
echo 5. Refresh the page (F5)
echo 6. Log in again
echo 7. Try uploading and annotating!
echo.
pause
