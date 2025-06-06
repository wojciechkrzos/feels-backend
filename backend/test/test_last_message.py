#!/usr/bin/env python3
"""
Test script to verify the last_message functionality in Chat model
"""
import requests
import json
import time
from config import BASE_URL

def test_last_message_functionality():
    print("📩 Testing Last Message Functionality")
    print("=" * 50)
    
    # Step 1: Create two test users
    print("\n👤 Step 1: Creating test users...")
    
    user1_data = {
        "username": "lastmsg_user1",
        "email": "lastmsg1@example.com", 
        "password": "testpass123",
        "display_name": "User One"
    }
    
    user2_data = {
        "username": "lastmsg_user2",
        "email": "lastmsg2@example.com",
        "password": "testpass123", 
        "display_name": "User Two"
    }
    
    # Create users
    for i, user_data in enumerate([user1_data, user2_data], 1):
        response = requests.post(f'{BASE_URL}/accounts/', json=user_data)
        if response.status_code == 201:
            print(f"✅ User {i} created successfully!")
        else:
            print(f"⚠️  User {i} might already exist")
    
    # Step 2: Authenticate users
    print("\n🔐 Step 2: Authenticating users...")
    
    # Authenticate User 1
    auth_data1 = {
        "action": "login",
        "username": "lastmsg_user1",
        "password": "testpass123"
    }
    
    response = requests.post(f'{BASE_URL}/auth/', json=auth_data1)
    if response.status_code == 200:
        user1_token = response.json().get('token')
        user1_headers = {'Authorization': f'Bearer {user1_token}'}
        print("✅ User 1 authenticated!")
    else:
        print(f"❌ Failed to authenticate User 1: {response.status_code}")
        return False
    
    # Authenticate User 2
    auth_data2 = {
        "action": "login", 
        "username": "lastmsg_user2",
        "password": "testpass123"
    }
    
    response = requests.post(f'{BASE_URL}/auth/', json=auth_data2)
    if response.status_code == 200:
        user2_token = response.json().get('token')
        user2_headers = {'Authorization': f'Bearer {user2_token}'}
        print("✅ User 2 authenticated!")
    else:
        print(f"❌ Failed to authenticate User 2: {response.status_code}")
        return False
    
    # Step 3: Create a chat
    print("\n💬 Step 3: Creating a chat...")
    chat_data = {
        "participant_usernames": ["lastmsg_user2"],
        "name": "Test Last Message Chat"
    }
    
    response = requests.post(f'{BASE_URL}/chats/', json=chat_data, headers=user1_headers)
    if response.status_code == 201:
        chat_info = response.json()
        chat_id = chat_info['uid']
        print(f"✅ Chat created successfully!")
        print(f"   Chat ID: {chat_id}")
        print(f"   Name: {chat_info['name']}")
        
        # Check that last_message is initially None
        if chat_info.get('last_message') is None:
            print("✅ Initial last_message is None as expected")
        else:
            print("⚠️  Expected last_message to be None initially")
    else:
        print(f"❌ Failed to create chat: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Step 4: Send first message
    print("\n📤 Step 4: Sending first message...")
    message1_data = {
        "text": "Hello! This is the first message.",
        "message_type": "text"
    }
    
    response = requests.post(f'{BASE_URL}/chats/{chat_id}/messages/', 
                           json=message1_data, headers=user1_headers)
    if response.status_code == 201:
        message1_info = response.json()
        print(f"✅ First message sent!")
        print(f"   Message: {message1_info['text']}")
    else:
        print(f"❌ Failed to send first message: {response.status_code}")
        return False
    
    # Step 5: Check chat details - should have last_message
    print("\n🔍 Step 5: Checking chat details after first message...")
    response = requests.get(f'{BASE_URL}/chats/{chat_id}/', headers=user1_headers)
    if response.status_code == 200:
        chat_info = response.json()
        if chat_info.get('last_message'):
            last_msg = chat_info['last_message']
            print(f"✅ Last message found!")
            print(f"   Text: {last_msg['text']}")
            print(f"   Sender: {last_msg['sender']['display_name']}")
            print(f"   Created: {last_msg['created_at']}")
        else:
            print("❌ Expected last_message to be present")
            return False
    else:
        print(f"❌ Failed to get chat details: {response.status_code}")
        return False
    
    # Step 6: Send second message
    print("\n📤 Step 6: Sending second message...")
    message2_data = {
        "text": "This is the second message - should become the new last message.",
        "message_type": "text"
    }
    
    response = requests.post(f'{BASE_URL}/chats/{chat_id}/messages/', 
                           json=message2_data, headers=user2_headers)
    if response.status_code == 201:
        message2_info = response.json()
        print(f"✅ Second message sent!")
        print(f"   Message: {message2_info['text']}")
    else:
        print(f"❌ Failed to send second message: {response.status_code}")
        return False
    
    # Step 7: Verify last_message updated
    print("\n🔍 Step 7: Verifying last_message updated...")
    response = requests.get(f'{BASE_URL}/chats/{chat_id}/', headers=user1_headers)
    if response.status_code == 200:
        chat_info = response.json()
        if chat_info.get('last_message'):
            last_msg = chat_info['last_message']
            print(f"✅ Last message updated!")
            print(f"   Text: {last_msg['text']}")
            print(f"   Sender: {last_msg['sender']['display_name']}")
            
            # Verify it's the second message
            if "second message" in last_msg['text']:
                print("✅ Confirmed: Last message is the most recent one")
            else:
                print("❌ Expected last message to be the second message")
                return False
        else:
            print("❌ Expected last_message to be present")
            return False
    else:
        print(f"❌ Failed to get updated chat details: {response.status_code}")
        return False
    
    # Step 8: Check chat list includes last_message
    print("\n📋 Step 8: Checking chat list includes last_message...")
    response = requests.get(f'{BASE_URL}/chats/', headers=user1_headers)
    if response.status_code == 200:
        chats_response = response.json()
        chats = chats_response.get('chats', [])
        
        # Find our test chat
        test_chat = None
        for chat in chats:
            if chat['uid'] == chat_id:
                test_chat = chat
                break
        
        if test_chat and test_chat.get('last_message'):
            print("✅ Chat list includes last_message!")
            print(f"   Last message: {test_chat['last_message']['text']}")
        else:
            print("❌ Chat list missing last_message")
            return False
    else:
        print(f"❌ Failed to get chat list: {response.status_code}")
        return False
    
    print("\n🎉 All tests passed! Last message functionality working correctly.")
    return True

if __name__ == "__main__":
    try:
        success = test_last_message_functionality()
        if success:
            print("\n✅ TEST PASSED: Last message functionality working!")
        else:
            print("\n❌ TEST FAILED: Issues found with last message functionality")
    except Exception as e:
        print(f"\n💥 TEST ERROR: {str(e)}")
