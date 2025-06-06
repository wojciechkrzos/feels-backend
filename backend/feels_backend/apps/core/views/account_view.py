from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import json

from ..models import Account
from ..authentication import hash_password, authenticate_request


def str_to_bool(val):
    return str(val).strip().lower() in ('true', '1', 'yes', 'on')


class AccountView(APIView):
    """API views for Account management"""



    @extend_schema(
        summary="Get account details or list accounts",
        description="Retrieve a specific account by ID or list all accounts. Can filter by username, only_friends, exclude_friends.",
        parameters=[
            OpenApiParameter(
                name='username',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter accounts by username'
            ),
            OpenApiParameter(
                name='only_friends',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Return only friends of the authenticated user'
            ),
            OpenApiParameter(
                name='exclude_friends',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Exclude friends and self from the account list'
            ),
        ],
        responses={
            200: {
                "description": "Account details or list of accounts",
                "examples": {
                    "single_account": {
                        "uid": "acc_123",
                        "username": "johndoe",
                        "email": "john@example.com",
                        "display_name": "John Doe",
                        "bio": "Software developer",
                        "posts_read_count": 42,
                        "feelings_shared_count": 15,
                        "created_at": "2023-01-01T00:00:00Z",
                        "last_active": "2023-12-01T00:00:00Z"
                    },
                    "account_list": {
                        "accounts": [
                            {
                                "uid": "acc_123",
                                "username": "johndoe",
                                "display_name": "John Doe",
                                "feelings_shared_count": 15
                            }
                        ]
                    }
                }
            },
            404: {"description": "Account not found"},
            500: {"description": "Internal server error"}
        }
    )
    @authenticate_request
    def get(self, request, account_id=None):
        """Get account details or list accounts (secured, with exclude_friends/only_friends option)"""
        try:
            if account_id:
                account = Account.nodes.get(uid=account_id)
                return Response({
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
                username = request.GET.get('username')
                if username:
                    try:
                        account = Account.nodes.get(username=username)
                        return Response({
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
                        return Response({
                            'accounts': [],
                            'message': f'No account found with username: {username}'
                        })

                only_friends = str_to_bool(request.GET.get('only_friends', False))
                exclude_friends = str_to_bool(request.GET.get('exclude_friends', False))
                if only_friends and exclude_friends:
                    return Response({'error': 'Nie można jednocześnie użyć only_friends i exclude_friends.'},
                                        status=400)

                user = request.user_account
                if only_friends:
                    accounts = user.friends.all()
                else:
                    accounts = Account.nodes.all()
                    if exclude_friends:
                        friends = set(friend.uid for friend in user.friends.all())
                        accounts = [acc for acc in accounts if acc.uid != user.uid and acc.uid not in friends]

                return Response({
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
            return Response({'error': 'Account not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @extend_schema(
        summary="Create a new account",
        description="Register a new user account with username, email, and password",
        request={
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Unique username"},
                "email": {"type": "string", "format": "email", "description": "User email address"},
                "password": {"type": "string", "description": "User password"},
                "display_name": {"type": "string", "description": "Display name (optional)"},
                "bio": {"type": "string", "description": "User bio (optional)"}
            },
            "required": ["username", "email", "password"],
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securepassword123",
                "display_name": "John Doe",
                "bio": "Software developer"
            }
        },
        responses={
            201: {
                "description": "Account created successfully",
                "example": {
                    "uid": "acc_123",
                    "username": "johndoe",
                    "display_name": "John Doe",
                    "message": "Account created successfully"
                }
            },
            400: {
                "description": "Bad request - validation error",
                "examples": {
                    "username_exists": {"error": "Username already exists"},
                    "email_exists": {"error": "Email already exists"},
                    "missing_field": {"error": "Missing required field: 'username'"}
                }
            }
        }
    )
    def post(self, request):
        """Create a new account (public endpoint)"""
        try:
            data = json.loads(request.body)
            
            # Check if username already exists
            try:
                Account.nodes.get(username=data['username'])
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            except Account.DoesNotExist:
                pass
            
            # Check if email already exists
            try:
                Account.nodes.get(email=data['email'])
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            except Account.DoesNotExist:
                pass
            
            account = Account(
                username=data['username'],
                email=data['email'],
                display_name=data.get('display_name', ''),
                bio=data.get('bio', ''),
                password_hash=hash_password(data['password'])
            ).save()
            
            return Response({
                'uid': account.uid,
                'username': account.username,
                'display_name': account.display_name,
                'message': 'Account created successfully'
            }, status=status.HTTP_201_CREATED)
        except KeyError as e:
            return Response({'error': f'Missing required field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
