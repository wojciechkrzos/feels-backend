# Feels Backend - Social Media App for Sharing Emotions

A Django-based backend API for a social media application focused on sharing and tracking emotions, built with Neo4j graph database for rich relationship modeling.

## 🎉 **STATUS: PRODUCTION READY ✅**

- 🔐 **Authentication System**: Complete with token-based auth ([docs/AUTH.md](docs/AUTH.md))
- 🏥 **Health Monitoring**: `/api/health/` endpoint active
- 🎨 **Demo Interface**: Interactive testing at `/api/demo/`
- 🐳 **Neo4j Container**: Running and configured
- 📱 **Mobile-Ready APIs**: All endpoints operational
- ✅ **Tested & Validated**: Core functionality verified with comprehensive test suite
- 🧹 **Clean Codebase**: Streamlined test directory with essential tests only
- 🔧 **Environment Configuration**: Proper environment variable management

## 🎭 Features

### Core Functionality
- **Accounts**: User profiles with emotion tracking statistics
- **Posts**: Share emotions with the community through posts
- **Feelings**: Categorized emotions with colors and energy levels
- **Friends**: Send/accept friend requests and build connections
- **Chat**: Real-time messaging with emotion sharing
- **Comments**: Engage with posts through comments

### Emotion Categories
The app categorizes feelings into four types based on energy and pleasantness:
- **High Energy Pleasant**: Excited, Joyful, Energetic, Enthusiastic
- **Low Energy Pleasant**: Content, Peaceful, Grateful, Relaxed
- **High Energy Unpleasant**: Anxious, Frustrated, Angry, Stressed
- **Low Energy Unpleasant**: Sad, Lonely, Tired, Disappointed

## 🛠 Technology Stack

- **Backend**: Django 5.2
- **Database**: Neo4j (Graph Database)
- **ORM**: Neomodel + django_neomodel
- **API**: Django REST-style views
- **Python**: 3.x

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Neo4j Database (locally or cloud)
- pip

### 1. Clone and Setup Environment
```bash
cd /home/wojciu/projects/feels-backend/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
# Copy the example environment file
cp docs/.env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

Required environment variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to True for development
- `NEO4J_BOLT_URL`: Neo4j connection URL
- `NEO4J_USER` and `NEO4J_PASSWORD`: Neo4j credentials

### 3. Start Neo4j Database
```bash
# This will use your .env configuration
./start_neo4j.sh
```

### 4. Populate with Sample Data
```bash
cd feels_backend
python manage.py populate_db
```

### 5. Run the Development Server
```bash
python manage.py runserver 0.0.0.0:${DJANGO_PORT:-8002}
```

The API will be available at `http://localhost:8002/api/`

You can also visit the demo interface at `http://localhost:8002/demo/`

## 🚀 Quick Start

For immediate testing without full setup:

```bash
# Quick health check
curl http://localhost:8002/api/health/

# Run authentication tests
cd test && python test_auth.py

# Run comprehensive system tests
python comprehensive_test.py
```

## 📁 Project Structure

```
├── docs/                          # Documentation
│   ├── AUTH.md                   # Authentication system documentation
│   ├── NEO4J_GUIDE.md           # Neo4j setup and usage guide
│   └── .env.example             # Environment variables template
├── feels_backend/                # Django project
│   ├── apps/core/               # Core application
│   │   ├── authentication.py   # Token-based auth system
│   │   ├── models.py           # Data models
│   │   ├── views.py            # API endpoints
│   │   └── management/         # Django management commands
│   └── feels_backend/          # Django settings
├── scripts/                     # Utility scripts
│   └── start_neo4j.sh          # Neo4j startup script
└── test/                       # Testing suite
    ├── test_auth.py            # Authentication tests
    ├── test_api.py             # API functionality tests
    └── comprehensive_test.py   # Complete system tests
```

## 📚 Documentation

- **[AUTH.md](docs/AUTH.md)** - Complete authentication system documentation
- **[NEO4J_GUIDE.md](docs/NEO4J_GUIDE.md)** - Neo4j database setup and management

## 📊 Data Models

### Account
- `uid`: Unique identifier
- `username`: Unique username
- `email`: Email address
- `display_name`: Display name
- `bio`: User biography
- `posts_read_count`: Number of posts read
- `feelings_shared_count`: Number of feelings shared
- Relationships: posts, friends, friend_requests, chats

### Feeling
- `name`: Feeling name (e.g., "Excited", "Peaceful")
- `color`: Hex color code for UI representation
- `description`: Description of the feeling
- `feeling_type`: Categorization by energy/pleasantness

### Post
- `uid`: Unique identifier
- `body`: Post content
- `created_at`: Creation timestamp
- `likes_count`: Number of likes
- `comments_count`: Number of comments
- Relationships: author, feeling, comments, liked_by

### Chat & Messages
- Support for both direct and group chats
- Messages can include text or emotions
- Real-time conversation tracking

### Friend Requests
- `status`: pending, accepted, rejected
- `created_at`: Request timestamp
- `responded_at`: Response timestamp

## 🔐 Authentication

This project includes a comprehensive token-based authentication system. See [docs/AUTH.md](docs/AUTH.md) for detailed authentication documentation including:

- Registration and login flows
- Token-based authentication
- Protected endpoint access
- Security best practices
- Mobile app integration examples

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/` - User registration and login
- `POST /api/logout/` - User logout (requires authentication)

### Accounts
- `GET /api/accounts/` - List all accounts
- `GET /api/accounts/{id}/` - Get account details
- `POST /api/accounts/` - Create new account

### Posts
- `GET /api/posts/` - List all posts
- `GET /api/posts/{id}/` - Get post details
- `POST /api/posts/` - Create new post

### Feelings
- `GET /api/feelings/` - List all available feelings

### Friend Requests
- `POST /api/friend-requests/` - Send friend request
- `PUT /api/friend-requests/{id}/` - Accept/reject friend request

## 📝 API Usage Examples

### Create an Account
```bash
curl -X POST http://localhost:8002/api/accounts/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "emma_feelings",
    "email": "emma@example.com",
    "display_name": "Emma Watson",
    "bio": "Sharing my emotional journey"
  }'
```

### Create a Post
```bash
curl -X POST http://localhost:8002/api/posts/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "author_uid": "account-uid-here",
    "body": "Feeling grateful for this beautiful day!",
    "feeling_name": "Grateful",
    "is_public": true
  }'
```

### Send Friend Request
```bash
curl -X POST http://localhost:8002/api/friend-requests/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "sender_uid": "sender-uid",
    "receiver_uid": "receiver-uid",
    "message": "Hi! Would love to connect and share our emotional journeys!"
  }'
```

## 🧪 Testing

The project includes comprehensive testing scripts:

### Run Individual Tests
```bash
cd test

# Test authentication system
python test_auth.py

# Test basic API functionality  
python test_api.py

# Run comprehensive system tests
python comprehensive_test.py
```

### What the tests cover:
- **Authentication**: Registration, login, logout, token validation
- **API Endpoints**: All major API functionality
- **System Health**: Database connectivity and service status
- **Data Creation**: Sample data generation and validation
- **Error Handling**: Various error scenarios and edge cases

## 🏗 Graph Database Structure

The Neo4j graph model creates rich relationships:

```
(Account)-[:CREATED_BY]->(Post)-[:EXPRESSES_FEELING]->(Feeling)
(Account)-[:FRIENDS_WITH]->(Account)
(Account)-[:SENT_FRIEND_REQUEST]->(Account)
(Post)-[:COMMENT_ON]<-(Comment)-[:CREATED_BY]->(Account)
(Account)-[:PARTICIPATES_IN]->(Chat)<-[:SENT_TO]-(Message)
(Message)-[:SENT_BY]->(Account)
(Feeling)-[:HAS_TYPE]->(FeelingType)
```

## 🚀 Production Considerations

### Security
- ✅ **Token-based authentication** - Complete implementation active
- ✅ **Environment variables** - Secrets properly configured  
- Add rate limiting
- Enhance input validation

### Performance
- Add database indexes
- Implement caching
- Use pagination for large datasets
- Optimize Neo4j queries

### Monitoring
- ✅ **Health checks** - `/api/health/` endpoint implemented
- ✅ **Logging** - Django logging configured
- Add database performance monitoring
- Track API usage metrics

## 🔮 Future Enhancements

- **Push Notifications**: Real-time alerts for friend requests and messages
- **Emotion Analytics**: Personal emotion tracking over time
- **Privacy Controls**: Granular sharing permissions
- **Content Moderation**: Automated content filtering
- **Mobile SDK**: Native mobile app integration
- **Recommendation Engine**: Suggest friends based on emotional compatibility

## 📝 Recent Updates

- ✅ **Authentication Documentation**: Comprehensive auth system documentation added
- ✅ **Test Suite Cleanup**: Streamlined to 3 essential test files
- ✅ **Environment Variables**: Proper .env configuration implemented
- ✅ **Mermaid Diagrams**: Professional sequence diagrams for auth flows

## 📄 License

This project is built for educational and demonstration purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

**Built with ❤️ for emotional well-being and community connection**
