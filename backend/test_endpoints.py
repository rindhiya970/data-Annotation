#!/usr/bin/env python3
"""
Quick test script to verify all API endpoints are working.
Run this after starting the Flask server.

Usage:
    python test_endpoints.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def print_result(test_name, success, response=None, error=None):
    """Print test result with formatting."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    if response:
        print(f"   Status: {response.status_code}")
        try:
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"   Response: {response.text[:200]}")
    if error:
        print(f"   Error: {error}")

def test_signup():
    """Test user signup."""
    url = f"{BASE_URL}/auth/signup"
    email = f"test_{datetime.now().timestamp()}@example.com"
    data = {
        "email": email,
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=data)
        success = response.status_code == 201
        print_result("POST /api/auth/signup", success, response)
        return email if success else None
    except Exception as e:
        print_result("POST /api/auth/signup", False, error=str(e))
        return None

def test_login(email):
    """Test user login."""
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": email,
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=data)
        success = response.status_code == 200
        print_result("POST /api/auth/login", success, response)
        
        if success:
            return response.json().get('access_token')
        return None
    except Exception as e:
        print_result("POST /api/auth/login", False, error=str(e))
        return None

def test_protected_route(token):
    """Test protected route with JWT token."""
    url = f"{BASE_URL}/files"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        success = response.status_code == 200
        print_result("GET /api/files (Protected)", success, response)
        return success
    except Exception as e:
        print_result("GET /api/files (Protected)", False, error=str(e))
        return False

def test_cors():
    """Test CORS preflight request."""
    url = f"{BASE_URL}/auth/signup"
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        response = requests.options(url, headers=headers)
        success = response.status_code == 200
        print_result("OPTIONS /api/auth/signup (CORS)", success, response)
        
        # Check CORS headers
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }
        print(f"   CORS Headers: {json.dumps(cors_headers, indent=2)}")
        
        return success
    except Exception as e:
        print_result("OPTIONS /api/auth/signup (CORS)", False, error=str(e))
        return False

def test_invalid_login():
    """Test login with invalid credentials."""
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(url, json=data)
        success = response.status_code == 401
        print_result("POST /api/auth/login (Invalid Credentials)", success, response)
        return success
    except Exception as e:
        print_result("POST /api/auth/login (Invalid Credentials)", False, error=str(e))
        return False

def test_unauthorized_access():
    """Test accessing protected route without token."""
    url = f"{BASE_URL}/files"
    
    try:
        response = requests.get(url)
        success = response.status_code == 401
        print_result("GET /api/files (No Token)", success, response)
        return success
    except Exception as e:
        print_result("GET /api/files (No Token)", False, error=str(e))
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 API Endpoint Testing")
    print("=" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: CORS Preflight
    print("\n" + "=" * 60)
    print("Test 1: CORS Configuration")
    print("=" * 60)
    test_cors()
    
    # Test 2: Signup
    print("\n" + "=" * 60)
    print("Test 2: User Signup")
    print("=" * 60)
    email = test_signup()
    
    if not email:
        print("\n❌ Signup failed. Cannot continue with other tests.")
        return
    
    # Test 3: Login
    print("\n" + "=" * 60)
    print("Test 3: User Login")
    print("=" * 60)
    token = test_login(email)
    
    if not token:
        print("\n❌ Login failed. Cannot continue with protected route tests.")
        return
    
    # Test 4: Protected Route with Token
    print("\n" + "=" * 60)
    print("Test 4: Protected Route (With Token)")
    print("=" * 60)
    test_protected_route(token)
    
    # Test 5: Invalid Login
    print("\n" + "=" * 60)
    print("Test 5: Invalid Login Credentials")
    print("=" * 60)
    test_invalid_login()
    
    # Test 6: Unauthorized Access
    print("\n" + "=" * 60)
    print("Test 6: Unauthorized Access (No Token)")
    print("=" * 60)
    test_unauthorized_access()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\nIf all tests passed, your backend is properly configured!")
    print("You can now connect your frontend to the backend.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
