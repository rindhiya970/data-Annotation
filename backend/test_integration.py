"""
Quick integration test script to verify backend endpoints.
Run this after starting the Flask server to test all endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_response_format(response_data):
    """Verify response follows standardized format."""
    if isinstance(response_data, dict):
        if 'success' in response_data:
            assert 'message' in response_data, "Missing 'message' field"
            assert 'data' in response_data, "Missing 'data' field"
            print(f"  ✓ Response format valid: success={response_data['success']}")
            return True
    return False

def test_signup():
    """Test user signup endpoint."""
    print("\n1. Testing POST /api/auth/signup")
    
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
    print(f"  Status: {response.status_code}")
    
    data = response.json()
    test_response_format(data)
    
    return response.status_code in [201, 400]  # 400 if user already exists

def test_login():
    """Test user login endpoint."""
    print("\n2. Testing POST /api/auth/login")
    
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print(f"  Status: {response.status_code}")
    
    data = response.json()
    test_response_format(data)
    
    if response.status_code == 200 and data.get('success'):
        token = data['data']['access_token']
        print(f"  ✓ JWT Token received")
        return token
    
    return None

def test_list_files(token):
    """Test list files endpoint."""
    print("\n3. Testing GET /api/files")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/files", headers=headers)
    print(f"  Status: {response.status_code}")
    
    data = response.json()
    test_response_format(data)
    
    if response.status_code == 200 and data.get('success'):
        count = data['data']['count']
        print(f"  ✓ Found {count} files")

def test_list_videos(token):
    """Test list videos endpoint."""
    print("\n4. Testing GET /api/videos")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/videos", headers=headers)
    print(f"  Status: {response.status_code}")
    
    data = response.json()
    test_response_format(data)
    
    if response.status_code == 200 and data.get('success'):
        count = data['data']['count']
        print(f"  ✓ Found {count} videos")

def test_cors():
    """Test CORS preflight request."""
    print("\n5. Testing CORS (OPTIONS request)")
    
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Content-Type,Authorization"
    }
    
    response = requests.options(f"{BASE_URL}/files", headers=headers)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"  ✓ CORS preflight successful")
        print(f"  Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
        print(f"  Allow-Methods: {response.headers.get('Access-Control-Allow-Methods')}")

def main():
    """Run all integration tests."""
    print("=" * 60)
    print("Backend Integration Tests")
    print("=" * 60)
    print("\nMake sure Flask server is running on http://localhost:5000")
    print("Press Enter to continue...")
    input()
    
    try:
        # Test signup (may fail if user exists)
        test_signup()
        
        # Test login and get token
        token = test_login()
        
        if not token:
            print("\n❌ Login failed. Cannot continue with authenticated tests.")
            return
        
        # Test authenticated endpoints
        test_list_files(token)
        test_list_videos(token)
        
        # Test CORS
        test_cors()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to Flask server.")
        print("Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
