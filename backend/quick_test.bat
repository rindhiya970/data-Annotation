@echo off
echo ========================================
echo Quick Upload Test
echo ========================================
echo.
echo Make sure Flask server is running on http://localhost:5000
echo.

call venv\Scripts\activate.bat

echo Testing file upload...
python test_upload.py

pause
