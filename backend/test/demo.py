#!/usr/bin/env python3

def demo_models():
    """Demonstrate the model structure and relationships"""
    print("🎭 Feels Backend - Social Media for Emotions")
    print("=" * 60)
    
    print("\n📊 DATA MODEL OVERVIEW")
    print("-" * 30)
    
    print("\n👤 ACCOUNT MODEL:")
    print("   - uid: Unique identifier")
    print("   - username: Unique username")
    print("   - email: Email address")
    print("   - display_name: Display name")
    print("   - bio: User biography")
    print("   - posts_read_count: Statistics tracking")
    print("   - feelings_shared_count: Emotion sharing count")
    print("   - Relationships: posts, friends, chats, friend_requests")
    
    print("\n💙 FEELING MODEL:")
    print("   - name: Feeling name (e.g., 'Excited', 'Peaceful')")
    print("   - color: Hex color code for UI")
    print("   - description: Detailed description")
    print("   - feeling_type: Category (energy/pleasantness)")
    
    print("\n📝 POST MODEL:")
    print("   - uid: Unique identifier")
    print("   - body: Post content")
    print("   - created_at: Creation timestamp")
    print("   - likes_count: Engagement metrics")
    print("   - Relationships: author, feeling, comments")
    
    print("\n💬 CHAT & MESSAGE MODELS:")
    print("   - Support for group and direct chats")
    print("   - Messages can include emotions")
    print("   - Real-time conversation tracking")
    
    print("\n🤝 FRIEND REQUEST MODEL:")
    print("   - status: pending, accepted, rejected")
    print("   - message: Optional personal message")
    print("   - Bidirectional relationships")
    
    print("\n🌈 FEELING CATEGORIES:")
    categories = {
        "High Energy Pleasant": ["Excited", "Joyful", "Energetic", "Enthusiastic"],
        "Low Energy Pleasant": ["Content", "Peaceful", "Grateful", "Relaxed"],
        "High Energy Unpleasant": ["Anxious", "Frustrated", "Angry", "Stressed"],
        "Low Energy Unpleasant": ["Sad", "Lonely", "Tired", "Disappointed"]
    }
    
    for category, feelings in categories.items():
        print(f"   🎨 {category}:")
        for feeling in feelings:
            print(f"      - {feeling}")
    
    print("\n🔗 GRAPH RELATIONSHIPS:")
    print("   (Account)-[:CREATED_BY]->(Post)-[:EXPRESSES_FEELING]->(Feeling)")
    print("   (Account)-[:FRIENDS_WITH]->(Account)")
    print("   (Account)-[:SENT_FRIEND_REQUEST]->(Account)")
    print("   (Post)-[:COMMENT_ON]<-(Comment)-[:CREATED_BY]->(Account)")
    print("   (Account)-[:PARTICIPATES_IN]->(Chat)<-[:SENT_TO]-(Message)")
    
    print("\n🚀 API ENDPOINTS:")
    endpoints = [
        ("GET /api/accounts/", "List all accounts"),
        ("POST /api/accounts/", "Create new account"),
        ("GET /api/accounts/{id}/", "Get account details"),
        ("GET /api/posts/", "List all posts"),
        ("POST /api/posts/", "Create new post"),
        ("GET /api/posts/{id}/", "Get post details"),
        ("GET /api/feelings/", "List all feelings"),
        ("POST /api/friend-requests/", "Send friend request"),
        ("PUT /api/friend-requests/{id}/", "Accept/reject request"),
    ]
    
    for endpoint, description in endpoints:
        print(f"   📡 {endpoint:<30} - {description}")
    
    print("\n💡 SAMPLE API USAGE:")
    print("""
    # Create an account
    curl -X POST http://localhost:8000/api/accounts/ \\
      -H "Content-Type: application/json" \\
      -d '{
        "username": "emma_feelings",
        "email": "emma@example.com",
        "display_name": "Emma Watson"
      }'
    
    # Create a post
    curl -X POST http://localhost:8000/api/posts/ \\
      -H "Content-Type: application/json" \\
      -d '{
        "author_uid": "account-uid-here",
        "body": "Feeling grateful today!",
        "feeling_name": "Grateful"
      }'
    
    # Send friend request
    curl -X POST http://localhost:8000/api/friend-requests/ \\
      -H "Content-Type: application/json" \\
      -d '{
        "sender_uid": "sender-uid",
        "receiver_uid": "receiver-uid",
        "message": "Hi! Let's connect!"
      }'
    """)
    
    print("\n🛠 TECHNOLOGY STACK:")
    print("   - Backend: Django 5.2")
    print("   - Database: Neo4j (Graph Database)")
    print("   - ORM: Neomodel + django_neomodel")
    print("   - API: Django REST-style views")
    print("   - Python: 3.x")
    
    print("\n📦 SETUP INSTRUCTIONS:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Start Neo4j: docker run -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j")
    print("   3. Install schema: python manage.py install_labels")
    print("   4. Populate data: python manage.py populate_db")
    print("   5. Run server: python manage.py runserver")
    
    print("\n🎉 Ready to share emotions and build connections!")

def show_sample_data():
    """Show what the sample data would look like"""
    print("\n📱 SAMPLE DATA PREVIEW:")
    print("-" * 30)
    
    sample_accounts = [
        {"username": "alice_feels", "display_name": "Alice Johnson", "feelings_shared": 5},
        {"username": "bob_emotions", "display_name": "Bob Smith", "feelings_shared": 3},
        {"username": "charlie_mood", "display_name": "Charlie Brown", "feelings_shared": 7},
    ]
    
    print("\n👥 Sample Accounts:")
    for acc in sample_accounts:
        print(f"   - {acc['username']} ({acc['display_name']}) - {acc['feelings_shared']} feelings shared")
    
    sample_posts = [
        {"author": "alice_feels", "text": "What a beautiful morning! Feeling so grateful.", "feeling": "Grateful", "color": "#96CEB4"},
        {"author": "bob_emotions", "text": "Just finished my workout and I am pumped!", "feeling": "Energetic", "color": "#EE964B"},
        {"author": "charlie_mood", "text": "Spent the evening reading. Such a peaceful way to end the day.", "feeling": "Peaceful", "color": "#45B7D1"},
    ]
    
    print("\n📝 Sample Posts:")
    for post in sample_posts:
        print(f"   - @{post['author']}: \"{post['text'][:50]}...\"")
        print(f"     💙 Feeling: {post['feeling']} ({post['color']})")
        print()

if __name__ == '__main__':
    demo_models()
    show_sample_data()
