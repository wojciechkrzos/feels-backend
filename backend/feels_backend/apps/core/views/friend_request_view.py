from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import json
from datetime import datetime

from ..models import Account, FriendRequest
from ..authentication import authenticate_request


class FriendRequestView(APIView):
    """API views for Friend Request management"""
    
    @extend_schema(
        summary="Get friend requests",
        description="Get friend requests for the authenticated user. Can filter by type (received, sent, or all).",
        parameters=[
            OpenApiParameter(
                name='type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Type of requests to retrieve: received, sent, or all (default: received)',
                enum=['received', 'sent', 'all']
            )
        ],
        responses={
            200: {
                "description": "List of friend requests",
                "example": {
                    "friend_requests": [
                        {
                            "uid": "req_123",
                            "sender": {
                                "uid": "acc_456",
                                "username": "johndoe",
                                "display_name": "John Doe"
                            },
                            "receiver": {
                                "uid": "acc_789",
                                "username": "janedoe",
                                "display_name": "Jane Doe"
                            },
                            "status": "pending",
                            "created_at": "2023-12-01T10:00:00Z"
                        }
                    ],
                    "type": "received",
                    "count": 1
                }
            },
            401: {"description": "Authentication required"},
            500: {"description": "Internal server error"}
        }
    )
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
            
            return Response({
                'friend_requests': requests_data,
                'count': len(requests_data)
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
    @extend_schema(
        summary="Send a friend request",
        description="Send a friend request to another user. Requires authentication.",
        request={
            "type": "object",
            "properties": {
                "receiver_uid": {"type": "string", "description": "UID of the user to send friend request to"},
                "message": {"type": "string", "description": "Optional message with the friend request"}
            },
            "required": ["receiver_uid"],
            "example": {
                "receiver_uid": "acc_789",
                "message": "Hi! I'd like to be friends."
            }
        },
        responses={
            201: {
                "description": "Friend request sent successfully",
                "example": {
                    "uid": "req_123",
                    "message": "Friend request sent successfully",
                    "receiver": {
                        "uid": "acc_789",
                        "username": "janedoe",
                        "display_name": "Jane Doe"
                    }
                }
            },
            400: {
                "description": "Bad request",
                "examples": {
                    "missing_field": {"error": "receiver_uid is required"},
                    "self_request": {"error": "Cannot send friend request to yourself"},
                    "already_friends": {"error": "You are already friends with this user"},
                    "request_exists": {"error": "Friend request already exists"}
                }
            },
            404: {"description": "Receiver account not found"},
            401: {"description": "Authentication required"}
        }
    )
    @authenticate_request
    def post(self, request):
        """Send a friend request (requires authentication)"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if 'receiver_uid' not in data:
                return Response({'error': 'receiver_uid is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Use authenticated user as sender
            sender = request.user_account
            
            # Get receiver account
            try:
                receiver = Account.nodes.get(uid=data['receiver_uid'])
            except Account.DoesNotExist:
                return Response({'error': 'Receiver account not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if trying to send request to self
            try:
                if sender.uid == receiver.uid:
                    return Response({'error': 'Cannot send friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)
            except AttributeError as e:
                return Response({'error': f'UID access error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Check if they are already friends
            try:
                if receiver in sender.friends.all():
                    return Response({'error': 'You are already friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f'Friends check error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Check if request already exists (in either direction)
            try:
                existing_requests = FriendRequest.nodes.filter(status='pending')
                for req in existing_requests:
                    req_sender = req.sender.single()
                    req_receiver = req.receiver.single()
                    if (req_sender.uid == sender.uid and req_receiver.uid == receiver.uid):
                        return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f'Existing request check error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Check if there's a pending request from the other user
            try:
                existing_requests = FriendRequest.nodes.filter(status='pending')
                for req in existing_requests:
                    req_sender = req.sender.single()
                    req_receiver = req.receiver.single()
                    if (req_sender.uid == receiver.uid and req_receiver.uid == sender.uid):
                        return Response({'error': 'This user has already sent you a friend request'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f'Reverse request check error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Create friend request
            friend_request = FriendRequest(
                message=data.get('message', ''),
                status='pending'
            ).save()
            
            friend_request.sender.connect(sender)
            friend_request.receiver.connect(receiver)
            
            return Response({
                'message': 'Friend request sent successfully',
                'receiver': {
                    'uid': receiver.uid,
                    'username': receiver.username,
                    'display_name': receiver.display_name
                }
            }, status=status.HTTP_201_CREATED)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Accept or reject a friend request",
        description="Respond to a friend request by accepting or rejecting it. Only the receiver can respond.",
        request={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string", 
                    "enum": ["accept", "reject"],
                    "description": "Action to take on the friend request"
                }
            },
            "required": ["action"],
            "example": {"action": "accept"}
        },
        responses={
            200: {
                "description": "Friend request responded to successfully",
                "examples": {
                    "accepted": {"message": "Friend request accepted"},
                    "rejected": {"message": "Friend request rejected"}
                }
            },
            400: {
                "description": "Bad request",
                "examples": {
                    "invalid_action": {"error": "Invalid action"},
                    "invalid_json": {"error": "Invalid JSON data"}
                }
            },
            403: {"description": "You can only respond to friend requests sent to you"},
            404: {"description": "Friend request not found"},
            401: {"description": "Authentication required"}
        }
    )
    @authenticate_request
    def put(self, request, request_id):
        """Accept or reject a friend request (requires authentication)"""
        try:
            data = json.loads(request.body)
            action = data.get('action')  # 'accept', 'reject'
            
            friend_request = FriendRequest.nodes.get(uid=request_id)
            
            # Check if the authenticated user is the receiver
            if friend_request.receiver.single().uid != request.user_account.uid:
                return Response({'error': 'You can only respond to friend requests sent to you'}, status=status.HTTP_403_FORBIDDEN)
            
            if action == 'accept':
                friend_request.status = 'accepted'
                friend_request.responded_at = datetime.now()
                friend_request.save()
                
                # Create friendship relationship
                sender = friend_request.sender.single()
                receiver = friend_request.receiver.single()
                sender.friends.connect(receiver)
                receiver.friends.connect(sender)
                
                return Response({'message': 'Friend request accepted'})
            
            elif action == 'reject':
                friend_request.status = 'rejected'
                friend_request.responded_at = datetime.now()
                friend_request.save()
                
                return Response({'message': 'Friend request rejected'})
            
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
