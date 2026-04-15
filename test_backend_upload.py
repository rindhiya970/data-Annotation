#!/usr/bin/env python3
"""
Test script to upload a file directly to the Flask backend
Run this from the backend directory: python test_backend_upload.py
"""

import requests
import os

# Test file path - create a dummy file if needed
test_file_path = 'test_image.txt'

# Create a test file if it doesn't exist
if not os.path.exists(test_file_path):
    with open(test_file_path, 'w') as f:
        f.write('This is a test file for upload')
    print(f"✅ Created test file: {test_file_path}")

# Backend URL
url = 'http://127.0.0.1:5000/api/files/upload'

print(f"\n{'='*60}")
print("Testing File Upload to Flask Backend")
print(f"{'='*60}\n")

print(f"📤 Uploading to: {url}")
print(f"📁 File: {test_file_path}")

try:
    # Open file and create multipart form data
    with open(test_file_path, 'rb') as f:
        files = {'file': (test_file_path, f, 'text/plain')}
        
        print(f"\n🔄 Sending POST request...")
        response = requests.post(url, files=files)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print(f"📊 Response Body:")
        print(response.text)
        
        if response.status_code == 201:
            print(f"\n✅ SUCCESS! File uploaded successfully")
            data = response.json()
            print(f"   File ID: {data.get('data', {}).get('id')}")
            print(f"   Stored as: {data.get('data', {}).get('stored_filename')}")
        else:
            print(f"\n❌ FAILED! Status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error message: {error_data.get('message')}")
            except:
                print(f"   Response: {response.text}")
                
except requests.exceptions.ConnectionError:
    print(f"\n❌ ERROR: Cannot connect to backend at {url}")
    print(f"   Make sure Flask is running: python run.py")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*60}\n")
