import requests
import json
import re

# Server URL
BASE_URL = "http://localhost:8000"

def get_tokens():
    """Get fresh login tokens for both user and admin"""
    
    print("🔄 Getting fresh login tokens...")
    
    # Login as regular user
    user_response = requests.post(f"{BASE_URL}/login", 
                                 headers={"Content-Type": "application/json"},
                                 json={"username": "testuser1234", "password": "password123"})
    
    # Login as admin
    admin_response = requests.post(f"{BASE_URL}/login",
                                  headers={"Content-Type": "application/json"}, 
                                  json={"username": "admin123", "password": "admin123"})
    
    if user_response.status_code == 200 and admin_response.status_code == 200:
        user_token = user_response.json()["session_token"]
        admin_token = admin_response.json()["session_token"]
        
        print(f"✅ User Token: {user_token}")
        print(f"✅ Admin Token: {admin_token}")
        
        # Update the REST file
        update_rest_file(user_token, admin_token)
        
        return user_token, admin_token
    else:
        print("❌ Login failed!")
        print(f"User response: {user_response.status_code} - {user_response.text}")
        print(f"Admin response: {admin_response.status_code} - {admin_response.text}")
        return None, None

def update_rest_file(user_token, admin_token):
    """Update the REST file with new tokens"""
    
    rest_file_path = "endpoint-tests/00-MASTER-ALL-TESTS.http"
    
    try:
        # Read the file
        with open(rest_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace user token
        content = re.sub(
            r'@userToken = .*',
            f'@userToken = {user_token}',
            content
        )
        
        # Replace admin token  
        content = re.sub(
            r'@adminToken = .*',
            f'@adminToken = {admin_token}',
            content
        )
        
        # Write back
        with open(rest_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ Updated {rest_file_path} with new tokens!")
        
    except Exception as e:
        print(f"❌ Error updating REST file: {e}")

if __name__ == "__main__":
    print("🚀 Auto Token Updater for Parking API")
    print("=====================================")
    
    user_token, admin_token = get_tokens()
    
    if user_token and admin_token:
        print("\n🎯 SUCCESS! Tokens updated in REST file.")
        print("You can now run any endpoint test without access denied errors!")
    else:
        print("\n❌ FAILED! Check if server is running on http://localhost:8000")
