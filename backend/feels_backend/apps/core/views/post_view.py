from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

from ..models import Account, Post, Feeling
from ..authentication import authenticate_request


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
                # Check if filtering by author (user)
                author_uid = request.GET.get('author_uid')
                if author_uid:
                    return self._get_posts_by_author(request, author_uid)
                
                # Return all posts if no filter
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
                    feeling = Feeling.nodes.filter(name=data['feeling_name']).first()
                    if feeling:
                        post.feeling.connect(feeling)
                        feeling_connected = True
                    else:
                        print(f"Feeling '{data['feeling_name']}' not found in database")
                except Exception as feeling_error:
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
    
    @authenticate_request
    def _get_posts_by_author(self, request, author_uid):
        """Get posts by a specific author (requires authentication and friendship)"""
        try:
            requesting_user = request.user_account
            
            # Get the target user (author whose posts are being requested)
            try:
                target_user = Account.nodes.get(uid=author_uid)
            except Account.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
            
            # If requesting posts from self, allow access
            if requesting_user.uid == target_user.uid:
                posts_query = Post.nodes.filter()
                posts = [post for post in posts_query if post.author.single().uid == target_user.uid]
            else:
                # Check if users are friends
                are_friends = target_user in requesting_user.friends.all()
                if not are_friends:
                    return JsonResponse({
                        'error': 'You can only view posts from users you are friends with'
                    }, status=403)
                
                # Get posts by the target user
                posts_query = Post.nodes.filter()
                posts = [post for post in posts_query if post.author.single().uid == target_user.uid]
            
            # Format posts data
            posts_data = []
            for post in posts:
                author = post.author.single()
                feeling = post.feeling.single()
                
                post_data = {
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
                }
                posts_data.append(post_data)
            
            # Sort by creation date (newest first)
            posts_data.sort(key=lambda x: x['created_at'], reverse=True)
            
            return JsonResponse({
                'posts': posts_data,
                'author': {
                    'uid': target_user.uid,
                    'username': target_user.username,
                    'display_name': target_user.display_name
                },
                'count': len(posts_data)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
