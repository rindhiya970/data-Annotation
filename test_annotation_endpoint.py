#!/usr/bin/env python3
"""Test annotation endpoint to verify it's working."""

import requests
import json

def test_annotation_endpoint():
    """Test if annotation endpoint returns 200 instead of 404."""
    
    # Test URL
    url = "http://127.0.0.1:5000/api/annotations/file/1"
    
    print(f"Testing: {url}")
    
    try:
        # Make request
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Annotation endpoint is working!")
            return True
        elif response.status_code == 404:
            print("❌ FAILED: Endpoint returns 404 - Flask not loading new code")
            return False
        else:
            print(f"⚠️  UNEXPECTED: Got status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Cannot connect to Flask server")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_annotation_endpoint()