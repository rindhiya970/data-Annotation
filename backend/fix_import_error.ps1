# ========================================
# Fix Import Error - Clean Cache Script
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 1: Stop Flask Server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Press Ctrl+C in the Flask terminal window to stop the server"
Write-Host "Then press Enter here to continue..."
Read-Host

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "STEP 2: Delete __pycache__ Folders" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Find and delete all __pycache__ folders
$pycacheFolders = Get-ChildItem -Path "." -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue

if ($pycacheFolders) {
    Write-Host "Found $($pycacheFolders.Count) __pycache__ folder(s):" -ForegroundColor Green
    foreach ($folder in $pycacheFolders) {
        Write-Host "  Deleting: $($folder.FullName)" -ForegroundColor Gray
        Remove-Item -Path $folder.FullName -Recurse -Force
    }
    Write-Host "✅ All __pycache__ folders deleted" -ForegroundColor Green
} else {
    Write-Host "No __pycache__ folders found" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "STEP 3: Delete .pyc Files" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Find and delete all .pyc files
$pycFiles = Get-ChildItem -Path "." -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue

if ($pycFiles) {
    Write-Host "Found $($pycFiles.Count) .pyc file(s):" -ForegroundColor Green
    foreach ($file in $pycFiles) {
        Write-Host "  Deleting: $($file.FullName)" -ForegroundColor Gray
        Remove-Item -Path $file.FullName -Force
    }
    Write-Host "✅ All .pyc files deleted" -ForegroundColor Green
} else {
    Write-Host "No .pyc files found" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "STEP 4: Verify file_service.py Exists" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

$fileServicePath = "app\services\file_service.py"
if (Test-Path $fileServicePath) {
    Write-Host "✅ File exists: $fileServicePath" -ForegroundColor Green
    Write-Host "File size: $((Get-Item $fileServicePath).Length) bytes" -ForegroundColor Gray
    Write-Host "Last modified: $((Get-Item $fileServicePath).LastWriteTime)" -ForegroundColor Gray
} else {
    Write-Host "❌ ERROR: File not found: $fileServicePath" -ForegroundColor Red
    Write-Host "This is a critical error!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "STEP 5: Check for Duplicate Files" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

$duplicates = Get-ChildItem -Path "." -Recurse -Filter "file_service.py" -ErrorAction SilentlyContinue

Write-Host "Found $($duplicates.Count) file_service.py file(s):" -ForegroundColor Green
foreach ($file in $duplicates) {
    Write-Host "  $($file.FullName)" -ForegroundColor Gray
}

if ($duplicates.Count -gt 1) {
    Write-Host "⚠️  WARNING: Multiple file_service.py files found!" -ForegroundColor Yellow
    Write-Host "Make sure you're editing the correct one in app\services\" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "STEP 6: Verify Virtual Environment" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment is activated" -ForegroundColor Green
    Write-Host "Path: $env:VIRTUAL_ENV" -ForegroundColor Gray
} else {
    Write-Host "❌ Virtual environment is NOT activated" -ForegroundColor Red
    Write-Host "Activating venv..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    if ($env:VIRTUAL_ENV) {
        Write-Host "✅ Virtual environment activated" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "STEP 7: Verify Function Exists in File" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

$fileContent = Get-Content $fileServicePath -Raw
if ($fileContent -match "def get_file_by_id") {
    Write-Host "✅ Function 'get_file_by_id' found in file_service.py" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: Function 'get_file_by_id' NOT found in file_service.py" -ForegroundColor Red
    Write-Host "The file may be corrupted or incomplete!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if ($fileContent -match "def save_uploaded_file") {
    Write-Host "✅ Function 'save_uploaded_file' found in file_service.py" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: Function 'save_uploaded_file' NOT found in file_service.py" -ForegroundColor Red
}

if ($fileContent -match "def get_user_files") {
    Write-Host "✅ Function 'get_user_files' found in file_service.py" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: Function 'get_user_files' NOT found in file_service.py" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "STEP 8: Test Import Manually" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "Testing import..." -ForegroundColor Gray
$testScript = @"
import sys
sys.path.insert(0, '.')
try:
    from app.services.file_service import get_file_by_id, save_uploaded_file, get_user_files
    print('✅ SUCCESS: All functions imported successfully')
    print('  - get_file_by_id:', get_file_by_id)
    print('  - save_uploaded_file:', save_uploaded_file)
    print('  - get_user_files:', get_user_files)
except ImportError as e:
    print('❌ IMPORT ERROR:', str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)
"@

$testScript | Out-File -FilePath "test_import.py" -Encoding UTF8
python test_import.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Import test passed!" -ForegroundColor Green
} else {
    Write-Host "❌ Import test failed!" -ForegroundColor Red
    Write-Host "Check the error message above" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Remove-Item "test_import.py" -ErrorAction SilentlyContinue

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "STEP 9: Ready to Restart Flask" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "✅ All checks passed!" -ForegroundColor Green
Write-Host "`nYou can now restart Flask server:" -ForegroundColor Cyan
Write-Host "  python run.py" -ForegroundColor White
Write-Host "`nOr run the full initialization:" -ForegroundColor Cyan
Write-Host "  python init_db.py" -ForegroundColor White
Write-Host "  python run.py" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Read-Host "`nPress Enter to exit"
