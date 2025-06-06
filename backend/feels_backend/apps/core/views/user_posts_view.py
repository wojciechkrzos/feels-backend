from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

from ..models import Account, Post
from ..authentication import authenticate_request


class UserPostsView(View):
    """API view for getting posts by a specific user"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    @authenticate_request
    def get(self, request, user_id):
        """Get posts by a specific user (requires authentication and friendship)"""
        try:
            requesting_user = request.user_account
            
            # Get the target user
            try:
                target_user = Account.nodes.get(uid=user_id)
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
                        'error': 'You can only view posts from users you are friends with',
                        'target_user': {
                            'uid': target_user.uid,
                            'username': target_user.username,
                            'display_name': target_user.display_name
                        }
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
