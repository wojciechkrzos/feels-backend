from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from ..models import Account, Post
from ..authentication import authenticate_request


class UserPostsView(APIView):
    """API view for getting posts by a specific user"""
    
    @extend_schema(
        summary="Get posts by a specific user",
        description="Retrieve all posts by a specific user. Requires authentication and friendship (unless viewing own posts).",
        responses={
            200: {
                "description": "List of user's posts",
                "example": {
                    "posts": [
                        {
                            "uid": "post_123",
                            "body": "Having a great day!",
                            "created_at": "2023-12-01T10:00:00Z",
                            "likes_count": 5,
                            "comments_count": 2,
                            "author": {
                                "uid": "acc_123",
                                "username": "johndoe",
                                "display_name": "John Doe"
                            },
                            "feeling": {
                                "name": "Happy",
                                "color": "#FFD700"
                            }
                        }
                    ],
                    "author": {
                        "uid": "acc_123",
                        "username": "johndoe",
                        "display_name": "John Doe"
                    },
                    "count": 1
                }
            },
            403: {"description": "Can only view posts from friends or self"},
            404: {"description": "User not found"},
            401: {"description": "Authentication required"}
        }
    )
    @authenticate_request
    def get(self, request, user_id):
        """Get posts by a specific user (requires authentication and friendship)"""
        try:
            requesting_user = request.user_account
            
            # Get the target user
            try:
                target_user = Account.nodes.get(uid=user_id)
            except Account.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # If requesting posts from self, allow access
            if requesting_user.uid == target_user.uid:
                posts_query = Post.nodes.filter()
                posts = [post for post in posts_query if post.author.single().uid == target_user.uid]
            else:
                # Check if users are friends
                are_friends = target_user in requesting_user.friends.all()
                if not are_friends:
                    return Response({
                        'error': 'You can only view posts from users you are friends with',
                        'target_user': {
                            'uid': target_user.uid,
                            'username': target_user.username,
                            'display_name': target_user.display_name
                        }
                    }, status=status.HTTP_403_FORBIDDEN)
                
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
            
            return Response({
                'posts': posts_data,
                'author': {
                    'uid': target_user.uid,
                    'username': target_user.username,
                    'display_name': target_user.display_name
                },
                'count': len(posts_data)
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
