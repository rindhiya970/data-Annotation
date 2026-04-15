"""
Test script for image annotation features.

Run with: python -m pytest tests/test_image_annotations.py
"""

import requests
import json

BASE_URL = "http://localhost:5000"

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"


def test_image_annotation_workflow():
    """Test complete image annotation workflow."""
    
    # Step 1: Login
    print("1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert login_response.status_code == 200
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Login successful")
    
    # Step 2: Upload image
    print("\n2. Uploading image...")
    with open("test_image.jpg", "rb") as f:
        files = {"file": f}
        upload_response = requests.post(
            f"{BASE_URL}/files/upload",
            files=files,
            headers=headers
        )
    assert upload_response.status_code == 201
    file_id = upload_response.json()['file_id']
    print(f"✓ Image uploaded (file_id: {file_id})")
    
    # Step 3: Create annotation on image
    print("\n3. Creating annotation on image...")
    annotation_data = {
        "file_id": file_id,
        "label": "person",
        "x": 100.0,
        "y": 150.0,
        "width": 200.0,
        "height": 300.0
    }
    create_response = requests.post(
        f"{BASE_URL}/annotations/image",
        json=annotation_data,
        headers=headers
    )
    assert create_response.status_code == 201
    annotation_id = create_response.json()['annotation']['id']
    print(f"✓ Annotation created (id: {annotation_id})")
    
    # Step 4: Get annotations for image
    print("\n4. Fetching annotations for image...")
    get_response = requests.get(
        f"{BASE_URL}/annotations/image/{file_id}",
        headers=headers
    )
    assert get_response.status_code == 200
    annotations = get_response.json()['annotations']
    assert len(annotations) == 1
    print(f"✓ Retrieved {len(annotations)} annotation(s)")
    
    # Step 5: Export annotated image
    print("\n5. Exporting annotated image...")
    export_response = requests.get(
        f"{BASE_URL}/export/annotated-image/{file_id}",
        headers=headers
    )
    assert export_response.status_code == 200
    assert export_response.headers['Content-Type'] == 'image/jpeg'
    
    # Save annotated image
    with open("annotated_image.jpg", "wb") as f:
        f.write(export_response.content)
    print("✓ Annotated image exported and saved")
    
    print("\n✅ All tests passed!")


def test_validation_errors():
    """Test validation error handling."""
    
    # Login
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Missing required fields
    print("\n1. Testing missing required fields...")
    response = requests.post(
        f"{BASE_URL}/annotations/image",
        json={"file_id": 1, "label": "test"},
        headers=headers
    )
    assert response.status_code == 400
    assert "Missing required fields" in response.json()['error']
    print("✓ Validation error caught")
    
    # Test 2: Invalid coordinates
    print("\n2. Testing invalid coordinates...")
    response = requests.post(
        f"{BASE_URL}/annotations/image",
        json={
            "file_id": 1,
            "label": "test",
            "x": -10.0,
            "y": 50.0,
            "width": 100.0,
            "height": 100.0
        },
        headers=headers
    )
    assert response.status_code == 400
    assert "X coordinate" in response.json()['error']
    print("✓ Invalid coordinate validation works")
    
    # Test 3: Non-existent file
    print("\n3. Testing non-existent file...")
    response = requests.post(
        f"{BASE_URL}/annotations/image",
        json={
            "file_id": 99999,
            "label": "test",
            "x": 10.0,
            "y": 10.0,
            "width": 100.0,
            "height": 100.0
        },
        headers=headers
    )
    assert response.status_code == 400
    assert "not found" in response.json()['error'].lower()
    print("✓ File not found validation works")
    
    print("\n✅ All validation tests passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("IMAGE ANNOTATION FEATURE TESTS")
    print("=" * 60)
    
    try:
        test_image_annotation_workflow()
        test_validation_errors()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
