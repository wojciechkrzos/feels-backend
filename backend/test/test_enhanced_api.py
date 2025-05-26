import requests
import json
import random
import string

BASE_URL = 'http://localhost:8002/api'

def random_string(length=8):
    """Generate a random string for testing"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def test_enhanced_api():
    """Test all API endpoints with enhanced features"""
    print("🧪 Enhanced API Testing")
    print("=" * 50)
    
    # Test 1: Create test accounts
    print("\n1. Creating test accounts...")
    
    user1_data = {
        'username': f'testuser1_{random_string(4)}',
        'email': f'test1_{random_string(4)}@example.com',
        'password': 'testpass123',
        'display_name': 'Test User One'
    }
    
    user2_data = {
        'username': f'testuser2_{random_string(4)}',
        'email': f'test2_{random_string(4)}@example.com',
        'password': 'testpass456',
        'display_name': 'Test User Two'
    }
    
    # Create accounts using public endpoint
    for i, user_data in enumerate([user1_data, user2_data], 1):
        response = requests.post(f'{BASE_URL}/accounts/', json=user_data)
        if response.status_code == 201:
            print(f"✅ User {i} account created successfully")
        else:
            print(f"❌ Failed to create user {i} account: {response.text}")
            return
    
    # Test 2: Authentication
    print("\n2. Testing authentication...")
    
    # Login user 1
    login1_response = requests.post(f'{BASE_URL}/auth/', json={
        'action': 'login',
        'username': user1_data['username'],
        'password': user1_data['password']
    })
    
    if login1_response.status_code == 200:
        user1_token = login1_response.json()['token']
        print(f"✅ User 1 logged in successfully")
    else:
        print(f"❌ User 1 login failed: {login1_response.text}")
        return
    
    # Login user 2
    login2_response = requests.post(f'{BASE_URL}/auth/', json={
        'action': 'login',
        'username': user2_data['username'],
        'password': user2_data['password']
    })
    
    if login2_response.status_code == 200:
        user2_token = login2_response.json()['token']
        print(f"✅ User 2 logged in successfully")
    else:
        print(f"❌ User 2 login failed: {login2_response.text}")
        return
    
    # Test 3: Get all accounts to find UIDs
    print("\n3. Getting account information...")
    accounts_response = requests.get(f'{BASE_URL}/accounts/')
    if accounts_response.status_code == 200:
        accounts = accounts_response.json()['accounts']
        user1_account = next((acc for acc in accounts if acc['username'] == user1_data['username']), None)
        user2_account = next((acc for acc in accounts if acc['username'] == user2_data['username']), None)
        
        if user1_account and user2_account:
            print(f"✅ Found both user accounts")
            user1_uid = user1_account['uid']
            user2_uid = user2_account['uid']
        else:
            print(f"❌ Could not find user accounts")
            return
    else:
        print(f"❌ Failed to get accounts: {accounts_response.text}")
        return
    
    # Test 4: Get feelings
    print("\n4. Testing feelings endpoint...")
    feelings_response = requests.get(f'{BASE_URL}/feelings/')
    if feelings_response.status_code == 200:
        feelings = feelings_response.json()['feelings']
        print(f"✅ Retrieved {len(feelings)} feelings")
        if feelings:
            feeling_name = feelings[0]['name']
    else:
        print(f"❌ Failed to get feelings: {feelings_response.text}")
        feeling_name = 'Happy'  # fallback
    
    # Test 5: Create posts
    print("\n5. Creating posts...")
    
    # User 1 creates a post
    post1_data = {
        'body': 'This is my first test post!',
        'feeling_name': feeling_name
    }
    
    post1_response = requests.post(f'{BASE_URL}/posts/', 
                                  json=post1_data,
                                  headers={'Authorization': f'Bearer {user1_token}'})
    
    if post1_response.status_code == 201:
        print(f"✅ User 1 created post successfully")
    else:
        print(f"❌ User 1 failed to create post: {post1_response.text}")
    
    # Test 6: Friend request management
    print("\n6. Testing friend request management...")
    
    # User 1 sends friend request to User 2
    friend_request_data = {
        'receiver_uid': user2_uid,
        'message': 'Hey, want to be friends?'
    }
    
    friend_request_response = requests.post(f'{BASE_URL}/friend-requests/', 
                                          json=friend_request_data,
                                          headers={'Authorization': f'Bearer {user1_token}'})
    
    if friend_request_response.status_code == 201:
        print(f"✅ Friend request sent successfully")
        friend_request_uid = friend_request_response.json()['uid']
    else:
        print(f"❌ Failed to send friend request: {friend_request_response.text}")
        return
    
    # Test 7: Get friend requests (received by User 2)
    print("\n7. Testing get friend requests...")
    
    received_requests_response = requests.get(f'{BASE_URL}/friend-requests/?type=received',
                                            headers={'Authorization': f'Bearer {user2_token}'})
    
    if received_requests_response.status_code == 200:
        received_requests = received_requests_response.json()['friend_requests']
        print(f"✅ User 2 has {len(received_requests)} received friend requests")
        
        if received_requests:
            request = received_requests[0]
            print(f"   Request from: {request['sender']['username']}")
            print(f"   Message: {request['message']}")
            print(f"   Status: {request['status']}")
    else:
        print(f"❌ Failed to get received friend requests: {received_requests_response.text}")
    
    # Test 8: Accept friend request
    print("\n8. Testing friend request acceptance...")
    
    accept_response = requests.put(f'{BASE_URL}/friend-requests/{friend_request_uid}/',
                                 json={'action': 'accept'},
                                 headers={'Authorization': f'Bearer {user2_token}'})
    
    if accept_response.status_code == 200:
        print(f"✅ Friend request accepted successfully")
    else:
        print(f"❌ Failed to accept friend request: {accept_response.text}")
    
    # Test 9: Get sent friend requests (by User 1)
    print("\n9. Testing get sent friend requests...")
    
    sent_requests_response = requests.get(f'{BASE_URL}/friend-requests/?type=sent',
                                        headers={'Authorization': f'Bearer {user1_token}'})
    
    if sent_requests_response.status_code == 200:
        sent_requests = sent_requests_response.json()['friend_requests']
        print(f"✅ User 1 has {len(sent_requests)} sent friend requests")
        
        if sent_requests:
            request = sent_requests[0]
            print(f"   Request to: {request['receiver']['username']}")
            print(f"   Status: {request['status']}")
    else:
        print(f"❌ Failed to get sent friend requests: {sent_requests_response.text}")
    
    # Test 10: Get profile information
    print("\n10. Testing profile endpoints...")
    
    profile1_response = requests.get(f'{BASE_URL}/profile/',
                                   headers={'Authorization': f'Bearer {user1_token}'})
    
    if profile1_response.status_code == 200:
        profile = profile1_response.json()['account']
        print(f"✅ User 1 profile retrieved successfully")
        print(f"   Username: {profile['username']}")
        print(f"   Display Name: {profile['display_name']}")
        print(f"   Feelings Shared: {profile['feelings_shared_count']}")
    else:
        print(f"❌ Failed to get user 1 profile: {profile1_response.text}")
    
    # Test 11: Logout
    print("\n11. Testing logout...")
    
    logout_response = requests.delete(f'{BASE_URL}/auth/',
                                    headers={'Authorization': f'Bearer {user1_token}'})
    
    if logout_response.status_code == 200:
        print(f"✅ User 1 logged out successfully")
    else:
        print(f"❌ Failed to logout user 1: {logout_response.text}")
    
    # Test 12: Try to access protected endpoint after logout
    print("\n12. Testing access after logout...")
    
    post_after_logout = requests.post(f'{BASE_URL}/posts/', 
                                    json={'body': 'This should fail'},
                                    headers={'Authorization': f'Bearer {user1_token}'})
    
    if post_after_logout.status_code == 401:
        print(f"✅ Access correctly denied after logout")
    else:
        print(f"❌ Access still allowed after logout: {post_after_logout.text}")
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced API testing completed!")

if __name__ == '__main__':
    test_enhanced_api()
