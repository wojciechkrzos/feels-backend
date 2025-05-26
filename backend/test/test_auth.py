#!/usr/bin/env python3
import requests
import json
from config import BASE_URL

def test_authentication():
    print("🔐 Testing Authentication System")
    print("=" * 50)
    
    # Test user registration
    print("\n📝 Testing user registration...")
    import time
    timestamp = str(int(time.time()))
    register_data = {
        "action": "register",
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "securepassword",
        "display_name": f"Test User {timestamp}"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/', json=register_data)
        if response.status_code == 201:
            data = response.json()
            token = data['token']
            user = data['user']
            print(f"✅ Registration successful!")
            print(f"   Token: {token[:20]}...")
            print(f"   User: {user['username']} ({user['display_name']})")
            
            # Test authenticated request
            print("\n🔒 Testing authenticated post creation...")
            headers = {'Authorization': f'Bearer {token}'}
            post_data = {
                "body": "My first authenticated post!",
                "feeling_name": "Excited"
            }
            
            post_response = requests.post(f'{BASE_URL}/posts/', json=post_data, headers=headers)
            if post_response.status_code == 201:
                print("✅ Authenticated post creation successful!")
                print(f"   Post ID: {post_response.json()['uid']}")
            else:
                print(f"❌ Post creation failed: {post_response.text}")
            
            # Test profile access
            print("\n👤 Testing profile access...")
            profile_response = requests.get(f'{BASE_URL}/profile/', headers=headers)
            if profile_response.status_code == 200:
                profile = profile_response.json()['user']
                print("✅ Profile access successful!")
                print(f"   Username: {profile['username']}")
                print(f"   Email: {profile['email']}")
                print(f"   Posts shared: {profile['feelings_shared_count']}")
            else:
                print(f"❌ Profile access failed: {profile_response.text}")
            
            # Test login
            print("\n🔑 Testing login...")
            login_data = {
                "action": "login",
                "username": "testuser123",
                "password": "securepassword"
            }
            
            login_response = requests.post(f'{BASE_URL}/auth/', json=login_data)
            if login_response.status_code == 200:
                login_data = login_response.json()
                print("✅ Login successful!")
                print(f"   New token: {login_data['token'][:20]}...")
            else:
                print(f"❌ Login failed: {login_response.text}")
            
            # Test logout
            print("\n🚪 Testing logout...")
            logout_response = requests.delete(f'{BASE_URL}/auth/', headers=headers)
            if logout_response.status_code == 200:
                print("✅ Logout successful!")
            else:
                print(f"❌ Logout failed: {logout_response.text}")
                
        else:
            print(f"❌ Registration failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django is running on port 8002")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print("\n🔗 Authentication Endpoints:")
    print(f"   POST {BASE_URL}/auth/ - Register/Login")
    print(f"   DELETE {BASE_URL}/auth/ - Logout")
    print(f"   GET {BASE_URL}/profile/ - Get profile (requires auth)")
    print(f"   PUT {BASE_URL}/profile/ - Update profile (requires auth)")
    print(f"   POST {BASE_URL}/posts/ - Create post (requires auth)")
    print(f"   POST {BASE_URL}/friend-requests/ - Send friend request (requires auth)")

if __name__ == '__main__':
    test_authentication()
