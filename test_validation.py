"""
Quick validation test script
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_validation():
    print("Testing validation...")
    
    # Test invalid email
    print("\n1. Testing invalid email:")
    response = requests.post(f"{BASE_URL}/identify", json={
        "email": "not-an-email",
        "phoneNumber": "+1234567890"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test invalid phone
    print("\n2. Testing invalid phone:")
    response = requests.post(f"{BASE_URL}/identify", json={
        "email": "test@example.com",
        "phoneNumber": "abc"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test valid data
    print("\n3. Testing valid data:")
    response = requests.post(f"{BASE_URL}/identify", json={
        "email": "valid@example.com",
        "phoneNumber": "+1234567890"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_validation()
