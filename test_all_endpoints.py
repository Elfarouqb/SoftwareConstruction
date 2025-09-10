import requests
import json
import time
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000"

# Results storage
results = []

def log_result(endpoint, method, description, response_code, response_data, error=None):
    """Log test result"""
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "endpoint": endpoint,
        "method": method,
        "description": description,
        "status_code": response_code,
        "response": response_data,
        "error": error
    }
    results.append(result)
    print(f"✅ {method} {endpoint} - {response_code} - {description}")

def test_endpoint(method, endpoint, description, data=None, headers=None, expect_error=False):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        try:
            response_data = response.json()
        except:
            response_data = response.text
            
        log_result(endpoint, method, description, response.status_code, response_data)
        return response
        
    except Exception as e:
        log_result(endpoint, method, description, "ERROR", None, str(e))
        return None

def main():
    print("🚀 Starting API Endpoint Testing...")
    print("=" * 60)
    
    # Store tokens
    user_token = None
    admin_token = None
    
    # 1. AUTHENTICATION TESTS
    print("\n📝 1. AUTHENTICATION ENDPOINTS")
    print("-" * 40)
    
    # Register User
    register_data = {
        "username": "testuser123",
        "password": "password123", 
        "name": "Test User"
    }
    test_endpoint("POST", "/register", "Register new user", register_data)
    
    # Register Admin
    admin_data = {
        "username": "admin123",
        "password": "admin123",
        "name": "Admin User"
    }
    test_endpoint("POST", "/register", "Register admin user", admin_data)
    
    # Login User
    login_data = {
        "username": "testuser123",
        "password": "password123"
    }
    response = test_endpoint("POST", "/login", "Login user", login_data)
    if response and response.status_code == 200:
        try:
            user_token = response.json().get("session_token")
            print(f"🔑 User Token: {user_token[:20]}...")
        except:
            pass
    
    # Login Admin  
    admin_login_data = {
        "username": "admin123",
        "password": "admin123"
    }
    response = test_endpoint("POST", "/login", "Login admin", admin_login_data)
    if response and response.status_code == 200:
        try:
            admin_token = response.json().get("session_token")
            print(f"🔑 Admin Token: {admin_token[:20]}...")
        except:
            pass
    
    # Login with wrong credentials
    wrong_login = {
        "username": "wronguser",
        "password": "wrongpass"
    }
    test_endpoint("POST", "/login", "Login with wrong credentials", wrong_login)
    
    # 2. PROFILE TESTS
    print("\n👤 2. PROFILE ENDPOINTS")
    print("-" * 40)
    
    if user_token:
        headers = {"Authorization": user_token}
        
        # Get Profile
        test_endpoint("GET", "/profile", "Get user profile", headers=headers)
        
        # Update Profile
        update_data = {
            "name": "Updated Test User",
            "password": "newpassword123"
        }
        test_endpoint("PUT", "/profile", "Update user profile", update_data, headers)
    else:
        print("❌ Skipping profile tests - no user token")
    
    # Test unauthorized access
    test_endpoint("GET", "/profile", "Get profile without token")
    
    # 3. PARKING LOTS TESTS
    print("\n🅿️ 3. PARKING LOTS ENDPOINTS")
    print("-" * 40)
    
    # Get all parking lots (public)
    test_endpoint("GET", "/parking-lots/", "Get all parking lots")
    
    # Get specific parking lot
    test_endpoint("GET", "/parking-lots/1", "Get parking lot by ID")
    
    if admin_token:
        admin_headers = {"Authorization": admin_token}
        
        # Create parking lot (admin only)
        parking_data = {
            "name": "Test Parking Lot",
            "location": "Test Street 123",
            "capacity": 100,
            "reserved": 0,
            "tariff": 2.50,
            "daytariff": 15.00
        }
        test_endpoint("POST", "/parking-lots", "Create parking lot (admin)", parking_data, admin_headers)
        
        # Update parking lot (admin only)
        update_parking = {
            "name": "Updated Parking Lot",
            "location": "New Street 456", 
            "capacity": 150,
            "reserved": 0,
            "tariff": 3.00,
            "daytariff": 20.00
        }
        test_endpoint("PUT", "/parking-lots/1", "Update parking lot (admin)", update_parking, admin_headers)
    
    # Test unauthorized parking lot operations
    if user_token:
        headers = {"Authorization": user_token}
        parking_data = {"name": "Unauthorized Parking", "capacity": 50}
        test_endpoint("POST", "/parking-lots", "Create parking lot (unauthorized)", parking_data, headers)
    
    # 4. VEHICLES TESTS
    print("\n🚗 4. VEHICLES ENDPOINTS")
    print("-" * 40)
    
    if user_token:
        headers = {"Authorization": user_token}
        
        # Register vehicle
        vehicle_data = {
            "name": "My Test Car",
            "license_plate": "ABC-123"
        }
        test_endpoint("POST", "/vehicles", "Register vehicle", vehicle_data, headers)
        
        # Get my vehicles
        test_endpoint("GET", "/vehicles", "Get my vehicles", headers=headers)
        
        # Vehicle entry
        entry_data = {
            "parkinglot": "1"
        }
        test_endpoint("POST", "/vehicles/ABC123/entry", "Vehicle entry", entry_data, headers)
        
        # Update vehicle
        update_vehicle = {
            "name": "My Updated Car"
        }
        test_endpoint("PUT", "/vehicles/ABC123", "Update vehicle", update_vehicle, headers)
        
        # Get vehicle reservations
        test_endpoint("GET", "/vehicles/ABC123/reservations", "Get vehicle reservations", headers=headers)
        
        # Get vehicle history
        test_endpoint("GET", "/vehicles/ABC123/history", "Get vehicle history", headers=headers)
    
    # Test unauthorized vehicle access
    test_endpoint("GET", "/vehicles", "Get vehicles without token")
    
    # 5. PARKING SESSIONS TESTS
    print("\n⏱️ 5. PARKING SESSIONS ENDPOINTS") 
    print("-" * 40)
    
    if user_token:
        headers = {"Authorization": user_token}
        
        # Start parking session
        session_data = {
            "licenseplate": "TEST-123"
        }
        test_endpoint("POST", "/parking-lots/1/sessions/start", "Start parking session", session_data, headers)
        
        # Get all sessions
        test_endpoint("GET", "/parking-lots/1/sessions", "Get all sessions", headers=headers)
        
        # Get specific session
        test_endpoint("GET", "/parking-lots/1/sessions/1", "Get specific session", headers=headers)
        
        # Stop parking session
        stop_data = {
            "licenseplate": "TEST-123"
        }
        test_endpoint("POST", "/parking-lots/1/sessions/stop", "Stop parking session", stop_data, headers)
    
    # 6. RESERVATIONS TESTS
    print("\n📅 6. RESERVATIONS ENDPOINTS")
    print("-" * 40)
    
    if user_token:
        headers = {"Authorization": user_token}
        
        # Create reservation
        reservation_data = {
            "licenseplate": "RES-123",
            "startdate": "2025-01-20",
            "enddate": "2025-01-21", 
            "parkinglot": "1"
        }
        test_endpoint("POST", "/reservations", "Create reservation", reservation_data, headers)
        
        # Get reservation
        test_endpoint("GET", "/reservations/1", "Get reservation", headers=headers)
        
        # Update reservation
        update_reservation = {
            "licenseplate": "RES-UPDATED",
            "startdate": "2025-01-20",
            "enddate": "2025-01-22",
            "parkinglot": "1"
        }
        test_endpoint("PUT", "/reservations/1", "Update reservation", update_reservation, headers)
        
        # Delete reservation
        test_endpoint("DELETE", "/reservations/1", "Delete reservation", headers=headers)
    
    # 7. PAYMENTS TESTS
    print("\n💳 7. PAYMENTS ENDPOINTS")
    print("-" * 40)
    
    if user_token:
        headers = {"Authorization": user_token}
        
        # Create payment
        payment_data = {
            "transaction": "TRX-123",
            "amount": 25.50
        }
        test_endpoint("POST", "/payments", "Create payment", payment_data, headers)
        
        # Get my payments
        test_endpoint("GET", "/payments", "Get my payments", headers=headers)
        
        # Complete payment
        complete_data = {
            "t_data": {
                "card_last4": "1234",
                "method": "credit_card"
            },
            "validation": "test_hash"
        }
        test_endpoint("PUT", "/payments/TRX-123", "Complete payment", complete_data, headers)
    
    if admin_token:
        admin_headers = {"Authorization": admin_token}
        
        # Create refund (admin only)
        refund_data = {
            "amount": 10.00,
            "transaction": "REFUND-123"
        }
        test_endpoint("POST", "/payments/refund", "Create refund (admin)", refund_data, admin_headers)
    
    # 8. BILLING TESTS
    print("\n🧾 8. BILLING ENDPOINTS") 
    print("-" * 40)
    
    if user_token:
        headers = {"Authorization": user_token}
        test_endpoint("GET", "/billing", "Get my billing", headers=headers)
    
    if admin_token:
        admin_headers = {"Authorization": admin_token}
        test_endpoint("GET", "/billing/testuser123", "Get user billing (admin)", headers=admin_headers)
    
    # 9. LOGOUT TESTS
    print("\n🔓 9. LOGOUT ENDPOINTS")
    print("-" * 40)
    
    if user_token:
        headers = {"Authorization": user_token}
        test_endpoint("GET", "/logout", "Logout user", headers=headers)
    
    if admin_token:
        admin_headers = {"Authorization": admin_token}
        test_endpoint("GET", "/logout", "Logout admin", headers=admin_headers)
    
    # 10. ERROR TESTS
    print("\n❌ 10. ERROR HANDLING TESTS")
    print("-" * 40)
    
    # Test non-existent endpoints
    test_endpoint("GET", "/nonexistent", "Non-existent endpoint")
    test_endpoint("POST", "/invalid", "Invalid endpoint", {})
    
    # Test malformed requests
    test_endpoint("POST", "/register", "Register with missing data", {"username": "test"})
    test_endpoint("POST", "/login", "Login with missing password", {"username": "test"})
    
    print("\n" + "=" * 60)
    print(f"🎉 Testing Complete! Total tests: {len(results)}")
    
    return results

if __name__ == "__main__":
    test_results = main()
