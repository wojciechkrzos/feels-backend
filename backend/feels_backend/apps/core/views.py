from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
from datetime import datetime

from .models import Account, Post, Feeling, FeelingType, Comment, Chat, Message, FriendRequest
from .authentication import authenticate_request


class AccountView(View):
    """API views for Account management"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, account_id=None):
        """Get account details or list accounts"""
        try:
            if account_id:
                account = Account.nodes.get(uid=account_id)
                return JsonResponse({
                    'uid': account.uid,
                    'username': account.username,
                    'email': account.email,
                    'display_name': account.display_name,
                    'bio': account.bio,
                    'posts_read_count': account.posts_read_count,
                    'feelings_shared_count': account.feelings_shared_count,
                    'created_at': str(account.created_at),
                    'last_active': str(account.last_active)
                })
            else:
                # Check if filtering by username
                username = request.GET.get('username')
                if username:
                    try:
                        account = Account.nodes.get(username=username)
                        return JsonResponse({
                            'accounts': [
                                {
                                    'uid': account.uid,
                                    'username': account.username,
                                    'display_name': account.display_name,
                                    'feelings_shared_count': account.feelings_shared_count
                                }
                            ]
                        })
                    except Account.DoesNotExist:
                        return JsonResponse({
                            'accounts': [],
                            'message': f'No account found with username: {username}'
                        })
                
                # Return all accounts if no filter
                accounts = Account.nodes.all()
                return JsonResponse({
                    'accounts': [
                        {
                            'uid': acc.uid,
                            'username': acc.username,
                            'display_name': acc.display_name,
                            'feelings_shared_count': acc.feelings_shared_count
                        } for acc in accounts
                    ]
                })
        except Account.DoesNotExist:
            return JsonResponse({'error': 'Account not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create a new account (public endpoint)"""
        try:
            data = json.loads(request.body)
            
            # Check if username already exists
            try:
                Account.nodes.get(username=data['username'])
                return JsonResponse({'error': 'Username already exists'}, status=400)
            except Account.DoesNotExist:
                pass  # Username is available
            
            # Check if email already exists
            try:
                Account.nodes.get(email=data['email'])
                return JsonResponse({'error': 'Email already exists'}, status=400)
            except Account.DoesNotExist:
                pass  # Email is available
            
            from .authentication import hash_password
            
            account = Account(
                username=data['username'],
                email=data['email'],
                display_name=data.get('display_name', ''),
                bio=data.get('bio', ''),
                password_hash=hash_password(data['password'])
            ).save()
            
            return JsonResponse({
                'uid': account.uid,
                'username': account.username,
                'display_name': account.display_name,
                'message': 'Account created successfully'
            }, status=201)
        except KeyError as e:
            return JsonResponse({'error': f'Missing required field: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class PostView(View):
    """API views for Post management"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, post_id=None):
        """Get post details or list posts"""
        try:
            if post_id:
                post = Post.nodes.get(uid=post_id)
                author = post.author.single()
                feeling = post.feeling.single()
                
                return JsonResponse({
                    'uid': post.uid,
                    'body': post.body,
                    'created_at': str(post.created_at),
                    'likes_count': post.likes_count,
                    'comments_count': post.comments_count,
                    'author': {
                        'uid': author.uid,
                        'username': author.username,
                        'display_name': author.display_name
                    },
                    'feeling': {
                        'name': feeling.name,
                        'color': feeling.color
                    } if feeling else None
                })
            else:
                posts = Post.nodes.all()
                posts_data = []
                for post in posts:
                    author = post.author.single()
                    feeling = post.feeling.single()
                    
                    post_data = {
                        'uid': post.uid,
                        'body': post.body[:100] + '...' if len(post.body) > 100 else post.body,
                        'created_at': str(post.created_at),
                        'likes_count': post.likes_count,
                        'comments_count': post.comments_count,
                        'author': {
                            'uid': author.uid if author else None,
                            'username': author.username if author else 'Unknown',
                            'display_name': author.display_name if author else 'Unknown'
                        },
                        'feeling': {
                            'name': feeling.name,
                            'color': feeling.color
                        } if feeling else None
                    }
                    posts_data.append(post_data)
                
                return JsonResponse({
                    'posts': posts_data
                })
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    @authenticate_request
    def post(self, request):
        """Create a new post (requires authentication)"""
        try:
            data = json.loads(request.body)
            
            # Use authenticated user as author
            author = request.user_account
            
            # Create the post
            post = Post(
                body=data['body'],
                is_public=data.get('is_public', True)
            ).save()
            
            # Connect to author
            post.author.connect(author)
            
            # Connect to feeling if provided
            feeling_connected = False
            if 'feeling_name' in data:
                try:
                    # Use filter().first() to handle potential duplicates
                    feeling = Feeling.nodes.filter(name=data['feeling_name']).first()
                    if feeling:
                        post.feeling.connect(feeling)
                        feeling_connected = True
                    else:
                        print(f"Feeling '{data['feeling_name']}' not found in database")
                except Exception as feeling_error:
                    # Log the feeling connection error but don't fail the post creation
                    print(f"Error connecting feeling '{data['feeling_name']}': {str(feeling_error)}")
            
            # Update author's feelings shared count
            author.feelings_shared_count += 1
            author.save()
            
            response_data = {
                'uid': post.uid,
                'message': 'Post created successfully'
            }
            
            if 'feeling_name' in data:
                response_data['feeling_connected'] = feeling_connected
                if not feeling_connected:
                    response_data['warning'] = f"Feeling '{data['feeling_name']}' not found or could not be connected"
            
            return JsonResponse(response_data, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class FeelingView(View):
    """API views for Feeling management"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """List all feelings"""
        try:
            feelings = Feeling.nodes.all()
            return JsonResponse({
                'feelings': [
                    {
                        'name': feeling.name,
                        'color': feeling.color,
                        'description': feeling.description,
                        'feeling_type': feeling.feeling_type.single().name if feeling.feeling_type.single() else None
                    } for feeling in feelings
                ]
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create a new feeling"""
        try:
            data = json.loads(request.body)
            
            feeling = Feeling(
                name=data['name'],
                color=data['color'],
                description=data.get('description', '')
            ).save()
            
            # Connect to feeling type if provided
            if 'feeling_type_name' in data:
                feeling_type = FeelingType.nodes.get(name=data['feeling_type_name'])
                feeling.feeling_type.connect(feeling_type)
            
            return JsonResponse({
                'name': feeling.name,
                'message': 'Feeling created successfully'
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class FriendRequestView(View):
    """API views for Friend Request management"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    @authenticate_request
    def get(self, request):
        """Get friend requests for authenticated user"""
        try:
            user = request.user_account
            request_type = request.GET.get('type', 'received')  # 'received', 'sent', or 'all'
            
            if request_type == 'received':
                # Get requests sent to this user - need to check all friend requests and filter manually
                all_requests = FriendRequest.nodes.all()
                friend_requests = []
                for req in all_requests:
                    receiver = req.receiver.single()
                    if receiver.uid == user.uid:
                        friend_requests.append(req)
            elif request_type == 'sent':
                # Get requests sent by this user - need to check all friend requests and filter manually
                all_requests = FriendRequest.nodes.all()
                friend_requests = []
                for req in all_requests:
                    sender = req.sender.single()
                    if sender.uid == user.uid:
                        friend_requests.append(req)
            else:
                # Get all requests involving this user
                all_requests = FriendRequest.nodes.all()
                friend_requests = []
                for req in all_requests:
                    sender = req.sender.single()
                    receiver = req.receiver.single()
                    if sender.uid == user.uid or receiver.uid == user.uid:
                        friend_requests.append(req)
            
            requests_data = []
            for req in friend_requests:
                sender = req.sender.single()
                receiver = req.receiver.single()
                requests_data.append({
                    'uid': req.uid,
                    'message': req.message,
                    'status': req.status,
                    'created_at': req.created_at.isoformat() if req.created_at else None,
                    'responded_at': req.responded_at.isoformat() if req.responded_at else None,
                    'sender': {
                        'uid': sender.uid,
                        'username': sender.username,
                        'display_name': sender.display_name
                    },
                    'receiver': {
                        'uid': receiver.uid,
                        'username': receiver.username,
                        'display_name': receiver.display_name
                    }
                })
            
            return JsonResponse({
                'friend_requests': requests_data,
                'count': len(requests_data)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    @authenticate_request
    def post(self, request):
        """Send a friend request (requires authentication)"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if 'receiver_uid' not in data:
                return JsonResponse({'error': 'receiver_uid is required'}, status=400)
            
            # Use authenticated user as sender
            sender = request.user_account
            
            # Get receiver account
            try:
                receiver = Account.nodes.get(uid=data['receiver_uid'])
            except Account.DoesNotExist:
                return JsonResponse({'error': 'Receiver account not found'}, status=404)
            
            # Check if trying to send request to self
            try:
                if sender.uid == receiver.uid:
                    return JsonResponse({'error': 'Cannot send friend request to yourself'}, status=400)
            except AttributeError as e:
                return JsonResponse({'error': f'UID access error: {str(e)}'}, status=500)
            
            # Check if they are already friends
            try:
                if receiver in sender.friends.all():
                    return JsonResponse({'error': 'You are already friends with this user'}, status=400)
            except Exception as e:
                return JsonResponse({'error': f'Friends check error: {str(e)}'}, status=500)
            
            # Check if request already exists (in either direction)
            try:
                existing_requests = FriendRequest.nodes.filter(status='pending')
                for req in existing_requests:
                    req_sender = req.sender.single()
                    req_receiver = req.receiver.single()
                    if (req_sender.uid == sender.uid and req_receiver.uid == receiver.uid):
                        return JsonResponse({'error': 'Friend request already sent'}, status=400)
            except Exception as e:
                return JsonResponse({'error': f'Existing request check error: {str(e)}'}, status=500)
            
            # Check if there's a pending request from the other user
            try:
                existing_requests = FriendRequest.nodes.filter(status='pending')
                for req in existing_requests:
                    req_sender = req.sender.single()
                    req_receiver = req.receiver.single()
                    if (req_sender.uid == receiver.uid and req_receiver.uid == sender.uid):
                        return JsonResponse({'error': 'This user has already sent you a friend request'}, status=400)
            except Exception as e:
                return JsonResponse({'error': f'Reverse request check error: {str(e)}'}, status=500)
            
            # Create friend request
            friend_request = FriendRequest(
                message=data.get('message', ''),
                status='pending'
            ).save()
            
            friend_request.sender.connect(sender)
            friend_request.receiver.connect(receiver)
            
            return JsonResponse({
                'message': 'Friend request sent successfully',
                'receiver': {
                    'uid': receiver.uid,
                    'username': receiver.username,
                    'display_name': receiver.display_name
                }
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    @authenticate_request
    def put(self, request, request_id):
        """Accept or reject a friend request (requires authentication)"""
        try:
            data = json.loads(request.body)
            action = data.get('action')  # 'accept' or 'reject'
            
            friend_request = FriendRequest.nodes.get(uid=request_id)
            
            # Check if the authenticated user is the receiver
            if friend_request.receiver.single().uid != request.user_account.uid:
                return JsonResponse({'error': 'You can only respond to friend requests sent to you'}, status=403)
            
            if action == 'accept':
                friend_request.status = 'accepted'
                friend_request.responded_at = datetime.now()
                friend_request.save()
                
                # Create friendship relationship
                sender = friend_request.sender.single()
                receiver = friend_request.receiver.single()
                sender.friends.connect(receiver)
                receiver.friends.connect(sender)
                
                return JsonResponse({'message': 'Friend request accepted'})
            
            elif action == 'reject':
                friend_request.status = 'rejected'
                friend_request.responded_at = datetime.now()
                friend_request.save()
                
                return JsonResponse({'message': 'Friend request rejected'})
            
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


# Create your views here.
