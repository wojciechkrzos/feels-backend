#!/usr/bin/env python3
import requests
import json
from datetime import datetime
from config import BASE_URL

def test_api():
    print("🎭 Testing Feels Backend API")
    print("=" * 50)
    
    # Test getting all accounts
    print("\n📱 Getting all accounts...")
    try:
        response = requests.get(f'{BASE_URL}/accounts/')
        if response.status_code == 200:
            accounts = response.json()['accounts']
            print(f"✅ Found {len(accounts)} accounts:")
            for acc in accounts[:3]:  # Show first 3
                print(f"   - {acc['username']} ({acc['display_name']}) - {acc['feelings_shared_count']} feelings shared")
        else:
            print(f"❌ Failed to get accounts: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the Django server is running!")
        return
    
    # Test getting all feelings
    print("\n💙 Getting all feelings...")
    response = requests.get(f'{BASE_URL}/feelings/')
    if response.status_code == 200:
        feelings = response.json()['feelings']
        print(f"✅ Found {len(feelings)} feelings:")
        for feeling in feelings[:5]:  # Show first 5
            print(f"   - {feeling['name']} ({feeling['color']}) - Type: {feeling['feeling_type']}")
    else:
        print(f"❌ Failed to get feelings: {response.status_code}")
    
    # Test getting all posts
    print("\n📝 Getting all posts...")
    response = requests.get(f'{BASE_URL}/posts/')
    if response.status_code == 200:
        posts = response.json()['posts']
        print(f"✅ Found {len(posts)} posts:")
        for post in posts[:3]:  # Show first 3
            print(f"   - By {post['author_username']}: \"{post['body']}\" ({post['likes_count']} likes)")
    else:
        print(f"❌ Failed to get posts: {response.status_code}")
    
    # Test creating a new account
    print("\n👤 Creating a new account...")
    new_account_data = {
        'username': 'test_user_' + str(int(datetime.now().timestamp())),
        'email': f'test_{int(datetime.now().timestamp())}@example.com',
        'display_name': 'Test User',
        'bio': 'I am a test user created by the API test script!'
    }
    
    response = requests.post(
        f'{BASE_URL}/accounts/',
        data=json.dumps(new_account_data),
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        new_account = response.json()
        print(f"✅ Created new account: {new_account['username']} (UID: {new_account['uid']})")
        
        # Test creating a post for the new account
        print("\n📝 Creating a post for the new account...")
        new_post_data = {
            'author_uid': new_account['uid'],
            'body': 'This is my first post! I am feeling excited to be part of this community.',
            'feeling_name': 'Excited',
            'is_public': True
        }
        
        response = requests.post(
            f'{BASE_URL}/posts/',
            data=json.dumps(new_post_data),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            new_post = response.json()
            print(f"✅ Created new post: {new_post['uid']}")
        else:
            print(f"❌ Failed to create post: {response.status_code} - {response.text}")
    else:
        print(f"❌ Failed to create account: {response.status_code} - {response.text}")
    
    print("\n🎉 API testing completed!")
    print("\nTo explore the API further, try these endpoints:")
    print(f"- GET {BASE_URL}/accounts/ - List all accounts")
    print(f"- GET {BASE_URL}/feelings/ - List all feelings")
    print(f"- GET {BASE_URL}/posts/ - List all posts")
    print(f"- POST {BASE_URL}/accounts/ - Create a new account")
    print(f"- POST {BASE_URL}/posts/ - Create a new post")
    print(f"- POST {BASE_URL}/friend-requests/ - Send a friend request")

if __name__ == '__main__':
    test_api()
