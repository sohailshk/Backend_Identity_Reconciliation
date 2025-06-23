"""
Advanced test script for contact merging scenarios.
This script demonstrates the complex merging logic where two primaries get merged.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_advanced_merging_scenario():
    """Test the advanced merging scenario where two primaries get merged."""
    
    print("🧪 Testing Advanced Contact Merging Scenario\n")
    
    # Step 1: Create primary A via email X
    print("📋 Step 1: Create Primary A with email X")
    primary_a_data = {"email": "primaryA@example.com"}
    
    response_a = requests.post(f"{BASE_URL}/identify", json=primary_a_data)
    print(f"Status: {response_a.status_code}")
    result_a = response_a.json()
    print(f"Primary A created: {json.dumps(result_a, indent=2)}")
    print()
    
    # Step 2: Create primary B via phone Y  
    print("📋 Step 2: Create Primary B with phone Y")
    primary_b_data = {"phoneNumber": "+5555555555"}
    
    response_b = requests.post(f"{BASE_URL}/identify", json=primary_b_data)
    print(f"Status: {response_b.status_code}")
    result_b = response_b.json()
    print(f"Primary B created: {json.dumps(result_b, indent=2)}")
    print()
    
    # Step 3: Send identify with email X and phone Y - should merge
    print("📋 Step 3: Link Primary A and B (should merge into single primary)")
    merge_data = {
        "email": "primaryA@example.com",
        "phoneNumber": "+5555555555"
    }
    
    response_merge = requests.post(f"{BASE_URL}/identify", json=merge_data)
    print(f"Status: {response_merge.status_code}")
    result_merge = response_merge.json()
    print(f"Merged result: {json.dumps(result_merge, indent=2)}")
    print()
    
    # Verify the merge worked correctly
    expected_primary_id = min(result_a["primaryContactId"], result_b["primaryContactId"])
    
    if result_merge["primaryContactId"] == expected_primary_id:
        print("✅ SUCCESS: Contacts merged correctly!")
        print(f"   - Primary Contact ID: {result_merge['primaryContactId']} (earliest created)")
        print(f"   - Total Emails: {len(result_merge['emails'])}")
        print(f"   - Total Phone Numbers: {len(result_merge['phoneNumbers'])}")
        print(f"   - Secondary Contacts: {len(result_merge['secondaryContactIds'])}")
        
        # Verify all data is consolidated
        assert "primaryA@example.com" in result_merge["emails"]
        assert "+5555555555" in result_merge["phoneNumbers"]
        assert len(result_merge["secondaryContactIds"]) >= 1  # At least the demoted primary
        
    else:
        print("❌ FAILURE: Merging did not work as expected")
        return False
    
    # Step 4: Test retrieving all contacts to see final state
    print("\n📋 Step 4: Check final database state")
    contacts_response = requests.get(f"{BASE_URL}/contacts")
    if contacts_response.status_code == 200:
        contacts = contacts_response.json()
        print(f"Total contacts in database: {len(contacts)}")
        
        primary_count = sum(1 for c in contacts if c["linkPrecedence"] == "primary")
        secondary_count = sum(1 for c in contacts if c["linkPrecedence"] == "secondary")
        
        print(f"Primary contacts: {primary_count}")
        print(f"Secondary contacts: {secondary_count}")
        
        if primary_count == 1:
            print("✅ SUCCESS: Only one primary contact remains after merge")
        else:
            print(f"❌ WARNING: Expected 1 primary, found {primary_count}")
    
    return True


def test_triple_merge_scenario():
    """Test merging three separate primaries through chained relationships."""
    
    print("\n🔄 Testing Triple Primary Merge Scenario\n")
    
    # Create three separate primaries
    print("📋 Creating three separate primary contacts")
    
    primary1_data = {"email": "user1@example.com"}
    primary2_data = {"phoneNumber": "+7777777777"}
    primary3_data = {"email": "user3@example.com"}
    
    resp1 = requests.post(f"{BASE_URL}/identify", json=primary1_data)
    resp2 = requests.post(f"{BASE_URL}/identify", json=primary2_data)
    resp3 = requests.post(f"{BASE_URL}/identify", json=primary3_data)
    
    print(f"Primary 1 ID: {resp1.json()['primaryContactId']}")
    print(f"Primary 2 ID: {resp2.json()['primaryContactId']}")
    print(f"Primary 3 ID: {resp3.json()['primaryContactId']}")
    
    # Link primary 1 and 2
    print("\n📋 Linking Primary 1 and 2")
    link12_data = {
        "email": "user1@example.com",
        "phoneNumber": "+7777777777"
    }
    link12_resp = requests.post(f"{BASE_URL}/identify", json=link12_data)
    print(f"After linking 1&2, primary ID: {link12_resp.json()['primaryContactId']}")
    
    # Link the merged group with primary 3
    print("\n📋 Linking merged group with Primary 3")
    link_all_data = {
        "email": "user3@example.com",
        "phoneNumber": "+7777777777"  # This should link all three
    }
    final_resp = requests.post(f"{BASE_URL}/identify", json=link_all_data)
    final_result = final_resp.json()
    
    print(f"Final merged result: {json.dumps(final_result, indent=2)}")
    
    # Verify all three groups are merged
    if len(final_result["emails"]) >= 2 and len(final_result["secondaryContactIds"]) >= 2:
        print("✅ SUCCESS: All three primaries successfully merged!")
    else:
        print("❌ FAILURE: Triple merge did not work correctly")
        return False
    
    return True


if __name__ == "__main__":
    try:
        # First check if server is running
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ Server is running, starting advanced tests...\n")
            
            # Run both test scenarios
            test1_success = test_advanced_merging_scenario()
            test2_success = test_triple_merge_scenario()
            
            if test1_success and test2_success:
                print("\n🎉 ALL ADVANCED TESTS PASSED!")
                print("The contact reconciliation system handles complex merging correctly.")
            else:
                print("\n❌ Some tests failed. Please check the implementation.")
                
        else:
            print("❌ Server is not responding. Please start the FastAPI server first.")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please make sure FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
