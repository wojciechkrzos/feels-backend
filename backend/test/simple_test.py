#!/usr/bin/env python3
import requests
import json
import time
from config import BASE_URL

def main():
    print("🚀 Testing Feels Backend API")
    print("=" * 40)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Status: {health['status']}")
            print(f"   ✅ Neo4j: {health['services']['neo4j']['status']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Feelings
    print("\n2. Testing Feelings...")
    try:
        response = requests.get(f"{BASE_URL}/feelings/", timeout=5)
        if response.status_code == 200:
            feelings = response.json()
            print(f"   ✅ Found {len(feelings['feelings'])} feelings")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Registration
    print("\n3. Testing Registration...")
    username = f"test_{int(time.time())}"
    register_data = {
        "action": "register",
        "username": username,
        "email": f"{username}@example.com",
        "password": "testpass123",
        "display_name": f"Test User {username}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/", json=register_data, timeout=5)
        if response.status_code == 201:
            print(f"   ✅ Registration successful")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Login
    print("\n4. Testing Login...")
    login_data = {
        "action": "login",
        "username": username,
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/", json=login_data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            token = result['token']
            print(f"   ✅ Login successful")
            
            # Test 5: Authenticated Post
            print("\n5. Testing Post Creation...")
            headers = {"Authorization": f"Bearer {token}"}
            post_data = {
                "body": f"Test post from {username} 🚀",
                "feeling_name": "Joyful"
            }
            
            response = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=headers, timeout=5)
            if response.status_code == 201:
                print(f"   ✅ Post created successfully")
            else:
                print(f"   ❌ Post failed: {response.status_code}")
                print(f"   Response: {response.text[:100]}")
                
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 40)
    print("✅ Basic API test completed!")
    print(f"🌐 Demo interface: {BASE_URL}/demo/")

if __name__ == "__main__":
    main()
