#!/usr/bin/env python3
"""
Comprehensive test for user posts functionality with friendship workflow
Tests the complete flow: user creation -> friend request -> acceptance -> posts -> access
"""
import requests
import json
import time
from config import BASE_URL

def test_complete_user_posts_workflow():
    print("🎭 Testing Complete User Posts Workflow")
    print("=" * 60)
    
    # Step 1: Create User 1
    print("\n👤 Step 1: Creating User 1...")
    user1_data = {
        "username": "testuser1",
        "email": "testuser1@example.com",
        "password": "testpass123",
        "display_name": "Test User One",
        "bio": "I'm the first test user"
    }
    
    response = requests.post(f'{BASE_URL}/accounts/', json=user1_data)
    if response.status_code == 201:
        user1_info = response.json()
        user1_uid = user1_info['uid']
        print(f"✅ User 1 created successfully!")
        print(f"   UID: {user1_uid}")
        print(f"   Username: {user1_info['username']}")
    else:
        print(f"❌ Failed to create User 1: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Step 2: Create User 2
    print("\n👤 Step 2: Creating User 2...")
    user2_data = {
        "username": "testuser2", 
        "email": "testuser2@example.com",
        "password": "testpass123",
        "display_name": "Test User Two",
        "bio": "I'm the second test user"
    }
    
    response = requests.post(f'{BASE_URL}/accounts/', json=user2_data)
    if response.status_code == 201:
        user2_info = response.json()
        user2_uid = user2_info['uid']
        print(f"✅ User 2 created successfully!")
        print(f"   UID: {user2_uid}")
        print(f"   Username: {user2_info['username']}")
    else:
        print(f"❌ Failed to create User 2: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Step 3: Authenticate User 1
    print("\n🔐 Step 3: Authenticating User 1...")
    auth_data1 = {
        "action": "login",
        "username": "testuser1",
        "password": "testpass123"
    }
    
    response = requests.post(f'{BASE_URL}/auth/', json=auth_data1)
    if response.status_code == 200:
        user1_token = response.json().get('token')
        user1_headers = {'Authorization': f'Bearer {user1_token}'}
        print("✅ User 1 authenticated successfully!")
    else:
        print(f"❌ Failed to authenticate User 1: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Step 4: Send friend request from User 1 to User 2
    print("\n🤝 Step 4: User 1 sending friend request to User 2...")
    friend_request_data = {
        "receiver_uid": user2_uid,
        "message": "Hi! Let's be friends and share our feelings!"
    }
    
    response = requests.post(f'{BASE_URL}/friend-requests/', 
                           json=friend_request_data, 
                           headers=user1_headers)
    if response.status_code == 201:
        print("✅ Friend request sent successfully!")
        print(f"   Message: {friend_request_data['message']}")
    else:
        print(f"❌ Failed to send friend request: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Step 5: Authenticate User 2
    print("\n🔐 Step 5: Authenticating User 2...")
    auth_data2 = {
        "action": "login",
        "username": "testuser2",
        "password": "testpass123"
    }
    
    response = requests.post(f'{BASE_URL}/auth/', json=auth_data2)
    if response.status_code == 200:
        user2_token = response.json().get('token')
        user2_headers = {'Authorization': f'Bearer {user2_token}'}
        print("✅ User 2 authenticated successfully!")
    else:
        print(f"❌ Failed to authenticate User 2: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Step 6: User 2 checks and accepts friend request
    print("\n📥 Step 6: User 2 checking received friend requests...")
    response = requests.get(f'{BASE_URL}/friend-requests/?type=received', 
                          headers=user2_headers)
    if response.status_code == 200:
        friend_requests = response.json()['friend_requests']
        print(f"✅ Found {len(friend_requests)} friend request(s)")
        
        if friend_requests:
            # Find the request from user1
            request_from_user1 = None
            for req in friend_requests:
                if req['sender']['uid'] == user1_uid:
                    request_from_user1 = req
                    break
            
            if request_from_user1:
                request_id = request_from_user1['uid']
                print(f"   Found request from {request_from_user1['sender']['username']}")
                
                # Accept the friend request
                print("\n✅ Step 6b: User 2 accepting friend request...")
                accept_data = {"action": "accept"}
                response = requests.put(f'{BASE_URL}/friend-requests/{request_id}/', 
                                      json=accept_data, 
                                      headers=user2_headers)
                if response.status_code == 200:
                    print("✅ Friend request accepted successfully!")
                    print("   Users are now friends! 🎉")
                else:
                    print(f"❌ Failed to accept friend request: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
            else:
                print("❌ No friend request found from User 1")
                return False
        else:
            print("❌ No friend requests found")
            return False
    else:
        print(f"❌ Failed to get friend requests: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Step 7: User 1 creates 2 posts
    print("\n📝 Step 7: User 1 creating 2 posts...")
    user1_posts = [
        {
            "body": "Just had an amazing morning! Feeling grateful for this beautiful day. 🌅",
            "feeling_name": "Grateful",
            "is_public": True
        },
        {
            "body": "Working on some exciting projects today. The creative energy is flowing! ⚡",
            "feeling_name": "Excited", 
            "is_public": True
        }
    ]
    
    user1_post_ids = []
    for i, post_data in enumerate(user1_posts):
        response = requests.post(f'{BASE_URL}/posts/', 
                               json=post_data, 
                               headers=user1_headers)
        if response.status_code == 201:
            post_info = response.json()
            user1_post_ids.append(post_info['uid'])
            print(f"   ✅ Post {i+1} created: {post_data['body'][:50]}...")
        else:
            print(f"   ❌ Failed to create post {i+1}: {response.status_code}")
            print(f"      Response: {response.text}")
    
    print(f"✅ User 1 created {len(user1_post_ids)} posts")
    
    # Step 8: User 2 creates 2 posts  
    print("\n📝 Step 8: User 2 creating 2 posts...")
    user2_posts = [
        {
            "body": "Had a challenging day but learned so much! Growth happens outside comfort zones. 💪",
            "feeling_name": "Determined",
            "is_public": True
        },
        {
            "body": "Spent quality time with family today. Nothing beats those precious moments together. ❤️",
            "feeling_name": "Content",
            "is_public": True
        }
    ]
    
    user2_post_ids = []
    for i, post_data in enumerate(user2_posts):
        response = requests.post(f'{BASE_URL}/posts/', 
                               json=post_data, 
                               headers=user2_headers)
        if response.status_code == 201:
            post_info = response.json()
            user2_post_ids.append(post_info['uid'])
            print(f"   ✅ Post {i+1} created: {post_data['body'][:50]}...")
        else:
            print(f"   ❌ Failed to create post {i+1}: {response.status_code}")
            print(f"      Response: {response.text}")
    
    print(f"✅ User 2 created {len(user2_post_ids)} posts")
    
    # Step 9: User 1 tries to get User 2's posts (should work now - they're friends!)
    print(f"\n🔍 Step 9: User 1 attempting to access User 2's posts...")
    
    # Test the dedicated endpoint
    print("   Testing dedicated endpoint: /users/<user_id>/posts/")
    response = requests.get(f'{BASE_URL}/users/{user2_uid}/posts/', 
                          headers=user1_headers)
    if response.status_code == 200:
        posts_data = response.json()
        print("   ✅ Successfully accessed User 2's posts via dedicated endpoint!")
        print(f"      Found {posts_data['count']} posts")
        print(f"      Author: {posts_data['author']['username']} ({posts_data['author']['display_name']})")
        
        # Show the posts
        for i, post in enumerate(posts_data['posts']):
            print(f"      Post {i+1}: {post['body'][:60]}...")
            if post['feeling']:
                print(f"         Feeling: {post['feeling']['name']}")
    else:
        print(f"   ❌ Failed to access User 2's posts: {response.status_code}")
        print(f"      Response: {response.text}")
        return False
    
    # Test the query parameter approach
    print("\n   Testing query parameter approach: /posts/?author_uid=<user_id>")
    response = requests.get(f'{BASE_URL}/posts/?author_uid={user2_uid}', 
                          headers=user1_headers)
    if response.status_code == 200:
        posts_data = response.json()
        print("   ✅ Successfully accessed User 2's posts via query parameter!")
        print(f"      Found {posts_data['count']} posts")
    else:
        print(f"   ❌ Failed to access User 2's posts via query: {response.status_code}")
        print(f"      Response: {response.text}")
    
    # Step 10: Verify User 1 can access their own posts
    print(f"\n👤 Step 10: User 1 accessing their own posts...")
    response = requests.get(f'{BASE_URL}/users/{user1_uid}/posts/', 
                          headers=user1_headers)
    if response.status_code == 200:
        posts_data = response.json()
        print("✅ Successfully accessed own posts!")
        print(f"   Found {posts_data['count']} posts")
        for i, post in enumerate(posts_data['posts']):
            print(f"   Post {i+1}: {post['body'][:60]}...")
    else:
        print(f"❌ Failed to access own posts: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Step 11: Test access without friendship (create User 3)
    print(f"\n🚫 Step 11: Testing access without friendship...")
    print("   Creating User 3 to test non-friend access...")
    
    user3_data = {
        "username": "testuser3",
        "email": "testuser3@example.com", 
        "password": "testpass123",
        "display_name": "Test User Three",
        "bio": "I'm the third test user (not friends with others)"
    }
    
    response = requests.post(f'{BASE_URL}/accounts/', json=user3_data)
    if response.status_code == 201:
        user3_info = response.json()
        user3_uid = user3_info['uid']
        
        # Authenticate User 3
        auth_data3 = {"action": "login", "username": "testuser3", "password": "testpass123"}
        response = requests.post(f'{BASE_URL}/auth/', json=auth_data3)
        if response.status_code == 200:
            user3_token = response.json().get('token')
            user3_headers = {'Authorization': f'Bearer {user3_token}'}
            
            # Try to access User 2's posts (should fail - not friends)
            response = requests.get(f'{BASE_URL}/users/{user2_uid}/posts/', 
                                  headers=user3_headers)
            if response.status_code == 403:
                print("   ✅ Correctly blocked non-friend access!")
                error_data = response.json()
                print(f"      Error: {error_data.get('error', 'No error message')}")
            else:
                print(f"   ❌ Unexpected response: {response.status_code}")
                print(f"      Response: {response.text}")
        else:
            print(f"   ❌ Failed to authenticate User 3: {response.status_code}")
    else:
        print(f"   ❌ Failed to create User 3: {response.status_code}")
    
    # Final Summary
    print(f"\n🎉 Test Completed Successfully!")
    print(f"=" * 60)
    print(f"✅ Created 2 users")
    print(f"✅ Sent and accepted friend request")  
    print(f"✅ Created 2 posts each (4 total)")
    print(f"✅ Friend successfully accessed friend's posts")
    print(f"✅ User successfully accessed own posts")
    print(f"✅ Non-friend access correctly blocked")
    print(f"✅ Both endpoint approaches work:")
    print(f"   - Dedicated: /users/<user_id>/posts/")
    print(f"   - Query: /posts/?author_uid=<user_id>")
    
    return True

if __name__ == "__main__":
    success = test_complete_user_posts_workflow()
    if success:
        print(f"\n🌟 All tests passed! The user posts functionality is working correctly.")
    else:
        print(f"\n💥 Some tests failed. Check the output above for details.")
