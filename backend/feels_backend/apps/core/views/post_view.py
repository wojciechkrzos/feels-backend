from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import json

from ..models import Account, Post, Feeling
from ..authentication import authenticate_request


class PostView(APIView):
    """API views for Post management"""
    
    @extend_schema(
        summary="Get post details or list posts",
        description="Retrieve a specific post by ID or list posts. Can filter by author.",
        parameters=[
            OpenApiParameter(
                name='author_uid',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter posts by author UID'
            )
        ],
        responses={
            200: {
                "description": "Post details or list of posts",
                "examples": {
                    "single_post": {
                        "uid": "post_123",
                        "body": "Feeling great today!",
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
                    },
                    "post_list": {
                        "posts": [
                            {
                                "uid": "post_123",
                                "body": "Feeling great!",
                                "created_at": "2023-12-01T10:00:00Z",
                                "likes_count": 5,
                                "author": {
                                    "username": "johndoe",
                                    "display_name": "John Doe"
                                }
                            }
                        ]
                    }
                }
            },
            404: {"description": "Post not found"},
            500: {"description": "Internal server error"}
        }
    )
    def get(self, request, post_id=None):
        """Get post details or list posts"""
        try:
            if post_id:
                post = Post.nodes.get(uid=post_id)
                author = post.author.single()
                feeling = post.feeling.single()
                
                return Response({
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
                
                return Response({
                    'posts': posts_data
                })
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Create a new post",
        description="Create a new post with optional feeling connection. Requires authentication.",
        request={
            "type": "object",
            "properties": {
                "body": {"type": "string", "description": "Post content"},
                "is_public": {"type": "boolean", "description": "Whether the post is public (default: true)"},
                "feeling_name": {"type": "string", "description": "Name of the feeling to associate with the post (optional)"}
            },
            "required": ["body"],
            "example": {
                "body": "Had a great day at the beach!",
                "is_public": True,
                "feeling_name": "Happy"
            }
        },
        responses={
            201: {
                "description": "Post created successfully",
                "example": {
                    "uid": "post_123",
                    "body": "Had a great day at the beach!",
                    "created_at": "2023-12-01T10:00:00Z",
                    "is_public": True,
                    "author": {
                        "uid": "acc_123",
                        "username": "johndoe",
                        "display_name": "John Doe"
                    },
                    "feeling": {
                        "name": "Happy",
                        "color": "#FFD700"
                    },
                    "message": "Post created successfully"
                }
            },
            400: {"description": "Bad request - validation error"},
            401: {"description": "Authentication required"}
        }
    )
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
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @authenticate_request
    def _get_posts_by_author(self, request, author_uid):
        """Get posts by a specific author (requires authentication and friendship)"""
        try:
            requesting_user = request.user_account
            
            # Get the target user (author whose posts are being requested)
            try:
                target_user = Account.nodes.get(uid=author_uid)
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
                        'error': 'You can only view posts from users you are friends with'
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
