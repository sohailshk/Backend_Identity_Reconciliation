"""
Test script for the /identify endpoint functionality.
This script demonstrates various scenarios for contact reconciliation.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_identify_endpoint():
    """Test the /identify endpoint with various scenarios."""
    
    print("🧪 Testing Contact Reconciliation /identify Endpoint\n")
    
    # Test 1: Create first contact (should become primary)
    print("📋 Test 1: New contact - should create primary")
    data1 = {
        "email": "john@example.com",
        "phoneNumber": "+1234567890"
    }
    
    response1 = requests.post(f"{BASE_URL}/identify", json=data1)
    print(f"Status: {response1.status_code}")
    result1 = response1.json()
    print(f"Response: {json.dumps(result1, indent=2)}")
    print()
    
    # Test 2: Same email, different phone (should link as secondary)
    print("📋 Test 2: Same email, different phone - should link as secondary")
    data2 = {
        "email": "john@example.com",
        "phoneNumber": "+0987654321"
    }
    
    response2 = requests.post(f"{BASE_URL}/identify", json=data2)
    print(f"Status: {response2.status_code}")
    result2 = response2.json()
    print(f"Response: {json.dumps(result2, indent=2)}")
    print()
    
    # Test 3: Same phone, different email (should link as secondary)
    print("📋 Test 3: Same phone, different email - should link as secondary")
    data3 = {
        "email": "john.doe@example.com",
        "phoneNumber": "+1234567890"
    }
    
    response3 = requests.post(f"{BASE_URL}/identify", json=data3)
    print(f"Status: {response3.status_code}")
    result3 = response3.json()
    print(f"Response: {json.dumps(result3, indent=2)}")
    print()
    
    # Test 4: Completely new contact (should create new primary)
    print("📋 Test 4: Completely new contact - should create new primary")
    data4 = {
        "email": "jane@example.com",
        "phoneNumber": "+5555555555"
    }
    
    response4 = requests.post(f"{BASE_URL}/identify", json=data4)
    print(f"Status: {response4.status_code}")
    result4 = response4.json()
    print(f"Response: {json.dumps(result4, indent=2)}")
    print()
    
    # Test 5: Email only
    print("📋 Test 5: Email only - should link to existing")
    data5 = {
        "email": "john@example.com"
    }
    
    response5 = requests.post(f"{BASE_URL}/identify", json=data5)
    print(f"Status: {response5.status_code}")
    result5 = response5.json()
    print(f"Response: {json.dumps(result5, indent=2)}")
    print()
    
    # Test 6: Phone only
    print("📋 Test 6: Phone only - should link to existing")
    data6 = {
        "phoneNumber": "+1234567890"
    }
    
    response6 = requests.post(f"{BASE_URL}/identify", json=data6)
    print(f"Status: {response6.status_code}")
    result6 = response6.json()
    print(f"Response: {json.dumps(result6, indent=2)}")
    print()
    
    # Test 7: Error case - no email or phone
    print("📋 Test 7: Error case - no email or phone")
    data7 = {}
    
    response7 = requests.post(f"{BASE_URL}/identify", json=data7)
    print(f"Status: {response7.status_code}")
    if response7.status_code != 200:
        print(f"Error Response: {response7.json()}")
    print()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    try:
        # First check if server is running
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ Server is running, starting tests...\n")
            test_identify_endpoint()
        else:
            print("❌ Server is not responding. Please start the FastAPI server first.")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please make sure FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
