"""Test file upload endpoint."""

import requests
import os

# API endpoint
API_URL = "http://localhost:5000/api/files/upload"

def test_upload(file_path):
    """Test uploading a file."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"\n📤 Uploading: {file_path}")
    print(f"📍 To: {API_URL}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(API_URL, files=files)
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📄 Response:")
        print(response.json())
        
        if response.status_code == 201:
            print("\n✅ Upload successful!")
        else:
            print("\n❌ Upload failed!")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to Flask server.")
        print("Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("File Upload Test")
    print("=" * 60)
    
    # Test with a sample file
    # Replace with actual file path on your system
    test_file = input("\nEnter path to test file (jpg, png, or mp4): ").strip()
    
    if test_file:
        test_upload(test_file)
    else:
        print("No file specified. Exiting.")
