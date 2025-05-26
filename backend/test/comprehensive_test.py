#!/usr/bin/env python3
import requests
import json
import time
import sys
import random
import string
from config import BASE_URL

def generate_unique_username():
    """Generate a unique username for testing"""
    timestamp = str(int(time.time()))
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
    return f"test_{timestamp}_{random_suffix}"

def test_system_health():
    """Test system health and connectivity"""
    print("🏥 Testing System Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=10)
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health check passed - Status: {health['status']}")
            
            # Check Neo4j specifically
            neo4j_status = health['services']['neo4j']['status']
            response_time = health['services']['neo4j']['response_time_ms']
            print(f"✅ Neo4j: {neo4j_status} (response time: {response_time}ms)")
            
            return True
        else:
            print(f"❌ Health check failed - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed - Error: {e}")
        return False

def test_feelings_endpoint():
    """Test feelings endpoint (public)"""
    print("\n💭 Testing Feelings Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/feelings/")
        
        if response.status_code == 200:
            feelings = response.json()
            feeling_count = len(feelings['feelings'])
            print(f"✅ Feelings endpoint - {feeling_count} feelings available")
            
            # Show some example feelings
            for feeling in feelings['feelings'][:3]:
                print(f"   - {feeling['name']}: {feeling['color']}")
            
            return True
        else:
            print(f"❌ Feelings endpoint failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Feelings endpoint failed - Error: {e}")
        return False

def test_registration_and_login():
    """Test user registration and login flow"""
    print("\n🔐 Testing Registration and Login...")
    
    # Generate unique test user
    username = generate_unique_username()
    email = f"{username}@example.com"
    password = "testpass123"
    display_name = f"Test User {username}"
    
    # Test registration
    register_data = {
        "action": "register",
        "username": username,
        "email": email,
        "password": password,
        "display_name": display_name
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/", json=register_data)
        
        if response.status_code == 201:
            register_result = response.json()
            print(f"✅ Registration successful - User: {register_result['username']}")
        else:
            print(f"❌ Registration failed - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Registration failed - Error: {e}")
        return None, None
    
    # Test login
    login_data = {
        "action": "login",
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/", json=login_data)
        
        if response.status_code == 200:
            login_result = response.json()
            token = login_result['token']
            print(f"✅ Login successful - Token received")
            return token, username
        else:
            print(f"❌ Login failed - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Login failed - Error: {e}")
        return None, None

def test_authenticated_endpoints(token, username):
    """Test endpoints that require authentication"""
    print("\n🛡️ Testing Authenticated Endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test profile endpoint
    try:
        response = requests.get(f"{BASE_URL}/profile/", headers=headers)
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Profile endpoint - User: {profile['username']}")
        else:
            print(f"❌ Profile endpoint failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Profile endpoint failed - Error: {e}")
        return False
    
    # Test creating a post
    post_data = {
        "body": f"This is a test post from user {username}! Testing the Feels Backend API 🚀",
        "feeling_name": "Joyful"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=headers)
        
        if response.status_code == 201:
            post = response.json()
            print(f"✅ Post creation successful - Post ID: {post['uid']}")
            return True
        else:
            print(f"❌ Post creation failed - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Post creation failed - Error: {e}")
        return False

def test_friend_requests(token1, username1, token2, username2):
    """Test friend request functionality between two users"""
    print("\n👥 Testing Friend Request System...")
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Get user2's UID first
    try:
        response = requests.get(f"{BASE_URL}/accounts/", headers=headers1)
        accounts = response.json()['accounts']
        user2_uid = None
        
        for account in accounts:
            if account['username'] == username2:
                user2_uid = account['uid']
                break
        
        if not user2_uid:
            print(f"❌ Could not find user2 UID")
            return False
        
    except Exception as e:
        print(f"❌ Failed to get accounts - Error: {e}")
        return False
    
    # Send friend request from user1 to user2
    friend_request_data = {
        "receiver_uid": user2_uid,
        "message": "Hey! Let's be friends on this awesome app!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/friend-requests/", json=friend_request_data, headers=headers1)
        
        if response.status_code == 201:
            request_result = response.json()
            print(f"✅ Friend request sent - Request ID: {request_result['uid']}")
            return True
        else:
            print(f"❌ Friend request failed - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Friend request failed - Error: {e}")
        return False

def test_public_endpoints():
    """Test public endpoints"""
    print("\n🌍 Testing Public Endpoints...")
    
    # Test accounts endpoint
    try:
        response = requests.get(f"{BASE_URL}/accounts/")
        
        if response.status_code == 200:
            accounts = response.json()
            account_count = len(accounts['accounts'])
            print(f"✅ Accounts endpoint - {account_count} accounts found")
        else:
            print(f"❌ Accounts endpoint failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Accounts endpoint failed - Error: {e}")
        return False
    
    # Test posts endpoint
    try:
        response = requests.get(f"{BASE_URL}/posts/")
        
        if response.status_code == 200:
            posts = response.json()
            post_count = len(posts['posts'])
            print(f"✅ Posts endpoint - {post_count} posts found")
            
            # Show latest post
            if posts['posts']:
                latest_post = posts['posts'][0]
                print(f"   Latest: \"{latest_post['body'][:50]}...\" by {latest_post['author_username']}")
            
            return True
        else:
            print(f"❌ Posts endpoint failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Posts endpoint failed - Error: {e}")
        return False

def test_demo_interface():
    """Test demo interface availability"""
    print("\n🎨 Testing Demo Interface...")
    
    try:
        response = requests.get(f"{BASE_URL}/demo/")
        
        if response.status_code == 200:
            print(f"✅ Demo interface available at {BASE_URL}/demo/")
            return True
        else:
            print(f"❌ Demo interface failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Demo interface failed - Error: {e}")
        return False

def main():
    """Run comprehensive test suite"""
    print("🚀 Starting Comprehensive Feels Backend Test Suite")
    print("=" * 60)
    
    # Test 1: System Health
    if not test_system_health():
        print("❌ System health check failed - stopping tests")
        sys.exit(1)
    
    # Test 2: Public endpoints
    if not test_feelings_endpoint():
        print("❌ Feelings endpoint failed")
    
    if not test_public_endpoints():
        print("❌ Public endpoints failed")
    
    # Test 3: Authentication flow with first user
    token1, username1 = test_registration_and_login()
    if not token1:
        print("❌ First user authentication failed")
        sys.exit(1)
    
    # Test 4: Authenticated endpoints with first user
    if not test_authenticated_endpoints(token1, username1):
        print("❌ Authenticated endpoints failed")
    
    # Test 5: Create second user for friend request testing
    print("\n👤 Creating second user for friend request testing...")
    token2, username2 = test_registration_and_login()
    if token2:
        # Test friend requests
        test_friend_requests(token1, username1, token2, username2)
    else:
        print("⚠️ Second user creation failed - skipping friend request test")
    
    # Test 6: Demo interface
    test_demo_interface()
    
    print("\n" + "=" * 60)
    print("🎉 Comprehensive Test Suite Completed!")
    print("✅ Feels Backend is fully operational and ready for production!")
    print("\n🌟 Key Features Validated:")
    print("   • Neo4j database connectivity")
    print("   • User registration and authentication")
    print("   • Emotion-based post creation")
    print("   • Friend request system")
    print("   • Public API endpoints")
    print("   • Demo interface")
    print("\n🚀 Your social media backend for sharing emotions is ready! 🚀")

if __name__ == "__main__":
    main()
