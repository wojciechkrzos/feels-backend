import secrets
import hashlib
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from functools import wraps

from .models import Account


class AuthToken:
    """Simple in-memory token storage (in production, use Redis or database)"""
    tokens = {}  # Format: {token: {'user_uid': 'xxx', 'expires': datetime}}
    
    @classmethod
    def create_token(cls, user_uid):
        """Create a new authentication token"""
        token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(hours=24)  # Token expires in 24 hours
        cls.tokens[token] = {
            'user_uid': user_uid,
            'expires': expires
        }
        return token
    
    @classmethod
    def validate_token(cls, token):
        """Validate a token and return user_uid if valid"""
        if token not in cls.tokens:
            return None
        
        token_data = cls.tokens[token]
        if datetime.now() > token_data['expires']:
            # Token expired, remove it
            del cls.tokens[token]
            return None
        
        return token_data['user_uid']
    
    @classmethod
    def revoke_token(cls, token):
        """Revoke a token (logout)"""
        if token in cls.tokens:
            del cls.tokens[token]


def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_request(view_func):
    """Decorator to require authentication for API endpoints"""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        token = auth_header.split(' ')[1]
        user_uid = AuthToken.validate_token(token)
        
        if not user_uid:
            return JsonResponse({'error': 'Invalid or expired token'}, status=401)
        
        # Add user info to request
        try:
            request.user_account = Account.nodes.get(uid=user_uid)
        except Account.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=401)
        
        return view_func(self, request, *args, **kwargs)
    
    return wrapper


class AuthView(View):
    """Authentication endpoints - register, login, logout"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        """Handle registration and login"""
        try:
            data = json.loads(request.body)
            action = data.get('action')  # 'register' or 'login'
            
            if action == 'register':
                return self.register(data)
            elif action == 'login':
                return self.login(data)
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def register(self, data):
        """Register a new user"""
        try:
            # Check if username already exists
            try:
                existing_user = Account.nodes.get(username=data['username'])
                return JsonResponse({'error': 'Username already exists'}, status=400)
            except Account.DoesNotExist:
                pass  # Username is available
            
            # Check if email already exists
            try:
                existing_email = Account.nodes.get(email=data['email'])
                return JsonResponse({'error': 'Email already exists'}, status=400)
            except Account.DoesNotExist:
                pass  # Email is available
            
            # Create new account
            account = Account(
                username=data['username'],
                email=data['email'],
                display_name=data.get('display_name', data['username']),
                bio=data.get('bio', ''),
                password_hash=hash_password(data['password'])
            ).save()
            
            # Create authentication token
            token = AuthToken.create_token(account.uid)
            
            return JsonResponse({
                'message': 'Registration successful',
                'token': token,
                'user': {
                    'uid': account.uid,
                    'username': account.username,
                    'display_name': account.display_name,
                    'email': account.email
                }
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'error': f'Registration failed: {str(e)}'}, status=400)
    
    def login(self, data):
        """Login an existing user"""
        try:
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return JsonResponse({'error': 'Username and password required'}, status=400)
            
            # Find user by username
            try:
                account = Account.nodes.get(username=username)
            except Account.DoesNotExist:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
            # Check password
            if account.password_hash != hash_password(password):
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
            # Update last active
            account.last_active = datetime.now()
            account.save()
            
            # Create authentication token
            token = AuthToken.create_token(account.uid)
            
            return JsonResponse({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'uid': account.uid,
                    'username': account.username,
                    'display_name': account.display_name,
                    'email': account.email,
                    'feelings_shared_count': account.feelings_shared_count
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Login failed: {str(e)}'}, status=400)
    
    def delete(self, request):
        """Logout - revoke token"""
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                AuthToken.revoke_token(token)
            
            return JsonResponse({'message': 'Logout successful'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class ProfileView(View):
    """User profile management"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    @authenticate_request
    def get(self, request):
        """Get current user's profile"""
        account = request.user_account
        return JsonResponse({
            'user': {
                'uid': account.uid,
                'username': account.username,
                'display_name': account.display_name,
                'email': account.email,
                'bio': account.bio,
                'feelings_shared_count': account.feelings_shared_count,
                'posts_read_count': account.posts_read_count,
                'created_at': str(account.created_at),
                'last_active': str(account.last_active)
            }
        })
    
    @authenticate_request
    def put(self, request):
        """Update current user's profile"""
        try:
            data = json.loads(request.body)
            account = request.user_account
            
            # Update allowed fields
            if 'display_name' in data:
                account.display_name = data['display_name']
            if 'bio' in data:
                account.bio = data['bio']
            if 'email' in data:
                # Check if email is already taken by another user
                existing = Account.nodes.filter(email=data['email']).first()
                if existing and existing.uid != account.uid:
                    return JsonResponse({'error': 'Email already in use'}, status=400)
                account.email = data['email']
            
            account.save()
            
            return JsonResponse({
                'message': 'Profile updated successfully',
                'user': {
                    'uid': account.uid,
                    'username': account.username,
                    'display_name': account.display_name,
                    'email': account.email,
                    'bio': account.bio
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
