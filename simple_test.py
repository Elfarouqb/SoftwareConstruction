import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000"

# Results storage
results = []

def test_endpoint(method, endpoint, description, data=None, headers=None):
    """Test a single endpoint and log results"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        # Prepare request
        if data:
            data_json = json.dumps(data).encode('utf-8')
        else:
            data_json = None
            
        req = urllib.request.Request(url, data=data_json, method=method)
        
        # Add headers
        req.add_header('Content-Type', 'application/json')
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        
        # Make request
        try:
            response = urllib.request.urlopen(req)
            response_code = response.getcode()
            response_text = response.read().decode('utf-8')
            
            try:
                response_data = json.loads(response_text)
            except:
                response_data = response_text
                
        except urllib.error.HTTPError as e:
            response_code = e.code
            response_text = e.read().decode('utf-8')
            try:
                response_data = json.loads(response_text)
            except:
                response_data = response_text
        
        # Log result
        result = {
            "endpoint": f"{method} {endpoint}",
            "description": description,
            "status_code": response_code,
            "response": response_data
        }
        results.append(result)
        
        print(f"✅ {method} {endpoint} - {response_code} - {description}")
        if isinstance(response_data, dict):
            if 'message' in response_data:
                print(f"   Message: {response_data['message']}")
            elif 'error' in response_data:
                print(f"   Error: {response_data['error']}")
        
        return response_code, response_data
        
    except Exception as e:
        result = {
            "endpoint": f"{method} {endpoint}",
            "description": description,
            "status_code": "ERROR",
            "response": str(e)
        }
        results.append(result)
        print(f"❌ {method} {endpoint} - ERROR - {str(e)}")
        return None, None

def main():
    print("🚀 Testing Parking API Endpoints")
    print("=" * 50)
    
    user_token = None
    admin_token = None
    
    # 1. Authentication Tests
    print("\n📝 Authentication Endpoints:")
    print("-" * 30)
    
    # Register user
    code, data = test_endpoint("POST", "/register", "Register new user", {
        "username": "testuser123",
        "password": "password123",
        "name": "Test User"
    })
    
    # Register admin
    test_endpoint("POST", "/register", "Register admin user", {
        "username": "admin123", 
        "password": "admin123",
        "name": "Admin User"
    })
    
    # Login user
    code, data = test_endpoint("POST", "/login", "Login user", {
        "username": "testuser123",
        "password": "password123"
    })
    
    if code == 200 and isinstance(data, dict) and 'session_token' in data:
        user_token = data['session_token']
        print(f"   🔑 User token obtained")
    
    # Login admin
    code, data = test_endpoint("POST", "/login", "Login admin", {
        "username": "admin123",
        "password": "admin123"
    })
    
    if code == 200 and isinstance(data, dict) and 'session_token' in data:
        admin_token = data['session_token']
        print(f"   🔑 Admin token obtained")
    
    # Test wrong login
    test_endpoint("POST", "/login", "Login with wrong credentials", {
        "username": "wronguser",
        "password": "wrongpass"
    })
    
    # 2. Profile Tests
    print("\n👤 Profile Endpoints:")
    print("-" * 30)
    
    if user_token:
        headers = {"Authorization": user_token}
        test_endpoint("GET", "/profile", "Get user profile", headers=headers)
        test_endpoint("PUT", "/profile", "Update user profile", {
            "name": "Updated User",
            "password": "newpass123"
        }, headers)
    
    test_endpoint("GET", "/profile", "Get profile without token")
    
    # 3. Parking Lots Tests
    print("\n🅿️ Parking Lots Endpoints:")
    print("-" * 30)
    
    test_endpoint("GET", "/parking-lots/", "Get all parking lots")
    test_endpoint("GET", "/parking-lots/1", "Get parking lot by ID")
    
    if admin_token:
        admin_headers = {"Authorization": admin_token}
        test_endpoint("POST", "/parking-lots", "Create parking lot (admin)", {
            "name": "Test Parking",
            "location": "Test Street 123",
            "capacity": 100,
            "reserved": 0,
            "tariff": 2.50,
            "daytariff": 15.00
        }, admin_headers)
        
        test_endpoint("PUT", "/parking-lots/1", "Update parking lot (admin)", {
            "name": "Updated Parking",
            "capacity": 150,
            "tariff": 3.00
        }, admin_headers)
    
    # 4. Vehicles Tests
    print("\n🚗 Vehicles Endpoints:")
    print("-" * 30)
    
    if user_token:
        headers = {"Authorization": user_token}
        test_endpoint("POST", "/vehicles", "Register vehicle", {
            "name": "My Car",
            "license_plate": "ABC-123"
        }, headers)
        
        test_endpoint("GET", "/vehicles", "Get my vehicles", headers=headers)
        test_endpoint("POST", "/vehicles/ABC123/entry", "Vehicle entry", {
            "parkinglot": "1"
        }, headers)
        test_endpoint("PUT", "/vehicles/ABC123", "Update vehicle", {
            "name": "My Updated Car"
        }, headers)
        test_endpoint("GET", "/vehicles/ABC123/reservations", "Get vehicle reservations", headers=headers)
        test_endpoint("GET", "/vehicles/ABC123/history", "Get vehicle history", headers=headers)
    
    test_endpoint("GET", "/vehicles", "Get vehicles without token")
    
    # 5. Sessions Tests
    print("\n⏱️ Parking Sessions Endpoints:")
    print("-" * 30)
    
    if user_token:
        headers = {"Authorization": user_token}
        test_endpoint("POST", "/parking-lots/1/sessions/start", "Start parking session", {
            "licenseplate": "TEST-123"
        }, headers)
        test_endpoint("GET", "/parking-lots/1/sessions", "Get all sessions", headers=headers)
        test_endpoint("GET", "/parking-lots/1/sessions/1", "Get specific session", headers=headers)
        test_endpoint("POST", "/parking-lots/1/sessions/stop", "Stop parking session", {
            "licenseplate": "TEST-123"
        }, headers)
    
    # 6. Reservations Tests
    print("\n📅 Reservations Endpoints:")
    print("-" * 30)
    
    if user_token:
        headers = {"Authorization": user_token}
        test_endpoint("POST", "/reservations", "Create reservation", {
            "licenseplate": "RES-123",
            "startdate": "2025-01-20",
            "enddate": "2025-01-21",
            "parkinglot": "1"
        }, headers)
        test_endpoint("GET", "/reservations/1", "Get reservation", headers=headers)
        test_endpoint("PUT", "/reservations/1", "Update reservation", {
            "licenseplate": "RES-UPDATED",
            "startdate": "2025-01-20",
            "enddate": "2025-01-22"
        }, headers)
        test_endpoint("DELETE", "/reservations/1", "Delete reservation", headers=headers)
    
    # 7. Payments Tests
    print("\n💳 Payments Endpoints:")
    print("-" * 30)
    
    if user_token:
        headers = {"Authorization": user_token}
        test_endpoint("POST", "/payments", "Create payment", {
            "transaction": "TRX-123",
            "amount": 25.50
        }, headers)
        test_endpoint("GET", "/payments", "Get my payments", headers=headers)
        test_endpoint("PUT", "/payments/TRX-123", "Complete payment", {
            "t_data": {"card_last4": "1234", "method": "credit_card"},
            "validation": "test_hash"
        }, headers)
    
    if admin_token:
        admin_headers = {"Authorization": admin_token}
        test_endpoint("POST", "/payments/refund", "Create refund (admin)", {
            "amount": 10.00,
            "transaction": "REFUND-123"
        }, admin_headers)
    
    # 8. Billing Tests
    print("\n🧾 Billing Endpoints:")
    print("-" * 30)
    
    if user_token:
        headers = {"Authorization": user_token}
        test_endpoint("GET", "/billing", "Get my billing", headers=headers)
    
    if admin_token:
        admin_headers = {"Authorization": admin_token}
        test_endpoint("GET", "/billing/testuser123", "Get user billing (admin)", headers=admin_headers)
    
    # 9. Logout Tests
    print("\n🔓 Logout Endpoints:")
    print("-" * 30)
    
    if user_token:
        headers = {"Authorization": user_token}
        test_endpoint("GET", "/logout", "Logout user", headers=headers)
    
    if admin_token:
        admin_headers = {"Authorization": admin_token}
        test_endpoint("GET", "/logout", "Logout admin", headers=admin_headers)
    
    # 10. Error Tests
    print("\n❌ Error Handling Tests:")
    print("-" * 30)
    
    test_endpoint("GET", "/nonexistent", "Non-existent endpoint")
    test_endpoint("POST", "/register", "Register with missing data", {"username": "test"})
    
    print("\n" + "=" * 50)
    print(f"🎉 Testing Complete! Total tests: {len(results)}")
    
    return results

if __name__ == "__main__":
    test_results = main()
    
    # Save to file
    output_file = "endpoint_test_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("PARKING API ENDPOINT TEST RESULTS\\n")
        f.write("=" * 50 + "\\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        f.write(f"Total Endpoints Tested: {len(test_results)}\\n\\n")
        
        for i, result in enumerate(test_results, 1):
            f.write(f"{i}. {result['endpoint']}\\n")
            f.write(f"   Description: {result['description']}\\n")
            f.write(f"   Status Code: {result['status_code']}\\n")
            f.write(f"   Response: {result['response']}\\n")
            f.write("-" * 50 + "\\n")
    
    print(f"\\n📄 Results saved to: {output_file}")
