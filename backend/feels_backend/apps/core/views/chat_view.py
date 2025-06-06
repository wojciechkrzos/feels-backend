from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import json
from datetime import datetime

from ..models import Account, Chat, Message, Feeling
from ..authentication import authenticate_request


class ChatView(APIView):
    """API views for Chat management"""
    
    @extend_schema(
        summary="Get chat details or list user's chats",
        description="Retrieve a specific chat by ID or list all chats the authenticated user participates in.",
        parameters=[
            OpenApiParameter(
                name='chat_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Specific chat ID to retrieve'
            )
        ],
        responses={
            200: {
                "description": "Chat details or list of chats",
                "examples": {
                    "single_chat": {
                        "uid": "chat_123",
                        "name": "Chat with John",
                        "is_group_chat": False,
                        "created_at": "2023-12-01T10:00:00Z",
                        "last_message_at": "2023-12-01T15:30:00Z",
                        "participants": [
                            {
                                "uid": "acc_123",
                                "username": "johndoe",
                                "display_name": "John Doe"
                            }
                        ],
                        "message_count": 15,
                        "last_message": {
                            "uid": "msg_456",
                            "text": "See you later!",
                            "message_type": "text",
                            "created_at": "2023-12-01T15:30:00Z",
                            "sender": {
                                "uid": "acc_123",
                                "username": "johndoe",
                                "display_name": "John Doe"
                            }
                        }
                    },
                    "chat_list": {
                        "chats": [
                            {
                                "uid": "chat_123",
                                "name": "Chat with John",
                                "is_group_chat": False,
                                "last_message_at": "2023-12-01T15:30:00Z",
                                "participants": ["johndoe"],
                                "unread_count": 3,
                                "last_message": {
                                    "uid": "msg_456",
                                    "text": "See you later!",
                                    "message_type": "text",
                                    "created_at": "2023-12-01T15:30:00Z",
                                    "sender": {
                                        "uid": "acc_123",
                                        "username": "johndoe",
                                        "display_name": "John Doe"
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            403: {"description": "Access denied - not a participant"},
            404: {"description": "Chat not found"},
            401: {"description": "Authentication required"}
        }
    )
    @authenticate_request
    def get(self, request, chat_id=None):
        """Get chat details or list user's chats"""
        try:
            user = request.user_account
            
            if chat_id:
                try:
                    chat = Chat.nodes.get(uid=chat_id)
                except Chat.DoesNotExist:
                    return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
                
                # Check if user is a participant
                participants = list(chat.participants.all())
                if user not in participants:
                    return Response({
                        'error': 'Access denied - you are not a participant in this chat'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                messages = list(chat.messages.all())
                last_message = chat.last_message.single() if chat.last_message.all() else None
                
                return Response({
                    'uid': chat.uid,
                    'name': chat.name,
                    'is_group_chat': chat.is_group_chat,
                    'created_at': str(chat.created_at),
                    'last_message_at': str(chat.last_message_at) if chat.last_message_at else None,
                    'participants': [
                        {
                            'uid': participant.uid,
                            'username': participant.username,
                            'display_name': participant.display_name
                        } for participant in participants
                    ],
                    'message_count': len(messages),
                    'last_message': {
                        'uid': last_message.uid,
                        'text': last_message.text,
                        'message_type': last_message.message_type,
                        'created_at': str(last_message.created_at),
                        'sender': {
                            'uid': last_message.sender.single().uid,
                            'username': last_message.sender.single().username,
                            'display_name': last_message.sender.single().display_name
                        } if last_message.sender.all() else None
                    } if last_message else None
                })
            else:
                # List all user's chats
                user_chats = list(user.chat_participants.all())
                
                chats_data = []
                for chat in user_chats:
                    participants = list(chat.participants.all())
                    messages = list(chat.messages.all())
                    last_message = chat.last_message.single() if chat.last_message.all() else None
                    
                    # Count unread messages for this user
                    unread_count = sum(1 for msg in messages if not msg.is_read and msg.sender.single().uid != user.uid)
                    
                    # Get other participants' usernames (exclude current user)
                    other_participants = [p.username for p in participants if p.uid != user.uid]
                    
                    chat_data = {
                        'uid': chat.uid,
                        'name': chat.name or f"Chat with {', '.join(other_participants)}",
                        'is_group_chat': chat.is_group_chat,
                        'created_at': str(chat.created_at),
                        'last_message_at': str(chat.last_message_at) if chat.last_message_at else None,
                        'participants': other_participants,
                        'unread_count': unread_count,
                        'message_count': len(messages),
                        'last_message': {
                            'uid': last_message.uid,
                            'text': last_message.text,
                            'message_type': last_message.message_type,
                            'created_at': str(last_message.created_at),
                            'sender': {
                                'uid': last_message.sender.single().uid,
                                'username': last_message.sender.single().username,
                                'display_name': last_message.sender.single().display_name
                            } if last_message.sender.all() else None
                        } if last_message else None
                    }
                    chats_data.append(chat_data)
                
                # Sort by last message time (most recent first)
                chats_data.sort(key=lambda x: x['last_message_at'] or '1900-01-01T00:00:00Z', reverse=True)
                
                return Response({
                    'chats': chats_data,
                    'count': len(chats_data)
                })
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Create a new chat",
        description="Create a new chat conversation with specified participants. Requires authentication.",
        request={
            "type": "object",
            "properties": {
                "participant_usernames": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of usernames to include in the chat"
                },
                "name": {"type": "string", "description": "Chat name (optional, auto-generated if not provided)"},
                "is_group_chat": {"type": "boolean", "description": "Whether this is a group chat (default: auto-detected)"}
            },
            "required": ["participant_usernames"],
            "example": {
                "participant_usernames": ["johndoe", "janedoe"],
                "name": "Weekend Plans",
                "is_group_chat": True
            }
        },
        responses={
            201: {
                "description": "Chat created successfully",
                "example": {
                    "uid": "chat_123",
                    "name": "Weekend Plans",
                    "is_group_chat": True,
                    "created_at": "2023-12-01T10:00:00Z",
                    "participants": [
                        {
                            "uid": "acc_123",
                            "username": "johndoe",
                            "display_name": "John Doe"
                        }
                    ],
                    "message": "Chat created successfully"
                }
            },
            400: {"description": "Bad request - validation error"},
            404: {"description": "One or more participants not found"},
            401: {"description": "Authentication required"}
        }
    )
    @authenticate_request
    def post(self, request):
        """Create a new chat (requires authentication)"""
        try:
            data = json.loads(request.body)
            user = request.user_account
            
            participant_usernames = data.get('participant_usernames', [])
            if not participant_usernames:
                return Response({
                    'error': 'At least one participant username is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find all participants
            participants = []
            not_found_users = []
            
            for username in participant_usernames:
                try:
                    participant = Account.nodes.get(username=username)
                    participants.append(participant)
                except Account.DoesNotExist:
                    not_found_users.append(username)
            
            if not_found_users:
                return Response({
                    'error': f'Users not found: {", ".join(not_found_users)}'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Add the requesting user if not already included
            if user not in participants:
                participants.append(user)
            
            is_group_chat = data.get('is_group_chat', len(participants) > 2)
            
            chat_name = data.get('name')
            if not chat_name:
                other_participants = [p.display_name or p.username for p in participants if p.uid != user.uid]
                if is_group_chat:
                    chat_name = f"Group with {', '.join(other_participants[:2])}"
                    if len(other_participants) > 2:
                        chat_name += f" and {len(other_participants) - 2} others"
                else:
                    chat_name = f"Chat with {other_participants[0] if other_participants else 'Unknown'}"
            
            # Create the chat
            chat = Chat(
                name=chat_name,
                is_group_chat=is_group_chat
            ).save()
            
            # Connect all participants
            for participant in participants:
                chat.participants.connect(participant)
            
            # Return chat details
            return Response({
                'uid': chat.uid,
                'name': chat.name,
                'is_group_chat': chat.is_group_chat,
                'created_at': str(chat.created_at),
                'participants': [
                    {
                        'uid': participant.uid,
                        'username': participant.username,
                        'display_name': participant.display_name
                    } for participant in participants
                ],
                'message': 'Chat created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MessageView(APIView):
    """API views for Message management within chats"""
    
    @extend_schema(
        summary="Get messages from a chat",
        description="Retrieve messages from a specific chat. Requires authentication and chat participation.",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of messages to return (default: 50)'
            ),
            OpenApiParameter(
                name='offset',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of messages to skip (default: 0)'
            ),
            OpenApiParameter(
                name='mark_as_read',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Mark messages as read (default: false)'
            )
        ],
        responses={
            200: {
                "description": "List of messages",
                "example": {
                    "messages": [
                        {
                            "uid": "msg_123",
                            "text": "Hey, how are you?",
                            "message_type": "text",
                            "created_at": "2023-12-01T10:00:00Z",
                            "is_read": True,
                            "sender": {
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
                    "count": 1,
                    "has_more": False
                }
            },
            403: {"description": "Access denied - not a chat participant"},
            404: {"description": "Chat not found"},
            401: {"description": "Authentication required"}
        }
    )
    @authenticate_request
    def get(self, request, chat_id):
        """Get messages from a chat"""
        try:
            user = request.user_account
            
            # Get chat and verify user is a participant
            try:
                chat = Chat.nodes.get(uid=chat_id)
            except Chat.DoesNotExist:
                return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
            
            participants = list(chat.participants.all())
            if user not in participants:
                return Response({
                    'error': 'Access denied - you are not a participant in this chat'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Pagination 
            limit = int(request.GET.get('limit', 50))
            offset = int(request.GET.get('offset', 0))
            mark_as_read = request.GET.get('mark_as_read', 'false').lower() == 'true'
            
            messages = list(chat.messages.all())
            
            messages.sort(key=lambda x: x.created_at, reverse=True)
            
            total_count = len(messages)
            paginated_messages = messages[offset:offset + limit]
            has_more = offset + limit < total_count
            
            # Format messages
            messages_data = []
            for message in paginated_messages:
                sender = message.sender.single()
                feeling = message.feeling.single() if message.feeling.all() else None
                
                message_data = {
                    'uid': message.uid,
                    'text': message.text,
                    'message_type': message.message_type,
                    'created_at': str(message.created_at),
                    'is_read': message.is_read,
                    'sender': {
                        'uid': sender.uid,
                        'username': sender.username,
                        'display_name': sender.display_name
                    },
                    'feeling': {
                        'name': feeling.name,
                        'color': feeling.color
                    } if feeling else None
                }
                messages_data.append(message_data)
                
                # Mark as read if requested and message is from another user
                if mark_as_read and sender.uid != user.uid and not message.is_read:
                    message.is_read = True
                    message.save()
            
            return Response({
                'messages': messages_data,
                'count': len(messages_data),
                'total_count': total_count,
                'has_more': has_more
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Send a message to a chat",
        description="Send a new message to a specific chat. Requires authentication and chat participation.",
        request={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Message text content"},
                "message_type": {
                    "type": "string",
                    "enum": ["text", "feeling", "image"],
                    "description": "Type of message (default: text)"
                },
                "feeling_name": {"type": "string", "description": "Name of feeling to associate (optional)"}
            },
            "required": ["text"],
            "example": {
                "text": "I'm having a great day!",
                "message_type": "feeling",
                "feeling_name": "Happy"
            }
        },
        responses={
            201: {
                "description": "Message sent successfully",
                "example": {
                    "uid": "msg_123",
                    "text": "I'm having a great day!",
                    "message_type": "feeling",
                    "created_at": "2023-12-01T10:00:00Z",
                    "sender": {
                        "uid": "acc_123",
                        "username": "johndoe",
                        "display_name": "John Doe"
                    },
                    "feeling": {
                        "name": "Happy",
                        "color": "#FFD700"
                    },
                    "message": "Message sent successfully"
                }
            },
            400: {"description": "Bad request - validation error"},
            403: {"description": "Access denied - not a chat participant"},
            404: {"description": "Chat not found"},
            401: {"description": "Authentication required"}
        }
    )
    @authenticate_request
    def post(self, request, chat_id):
        """Send a message to a chat"""
        try:
            data = json.loads(request.body)
            user = request.user_account
            
            # Get chat and verify user is a participant
            try:
                chat = Chat.nodes.get(uid=chat_id)
            except Chat.DoesNotExist:
                return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
            
            participants = list(chat.participants.all())
            if user not in participants:
                return Response({
                    'error': 'Access denied - you are not a participant in this chat'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Validate required fields
            if 'text' not in data or not data['text'].strip():
                return Response({
                    'error': 'Message text is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the message
            message = Message(
                text=data['text'],
                message_type=data.get('message_type', 'text')
            ).save()
            
            # Connect to sender and chat
            message.sender.connect(user)
            message.chat.connect(chat)
            
            # Connect to feeling if provided
            feeling_connected = None
            if 'feeling_name' in data:
                try:
                    feeling = Feeling.nodes.filter(name=data['feeling_name']).first()
                    if feeling:
                        message.feeling.connect(feeling)
                        feeling_connected = feeling
                except Exception as feeling_error:
                    print(f"Error connecting feeling '{data['feeling_name']}': {str(feeling_error)}")
            
            # Update chat's last message time and last message reference
            chat.last_message_at = datetime.now()
            
            # Disconnect previous last message if it exists
            if chat.last_message.all():
                chat.last_message.disconnect_all()
            
            # Connect new message as last message
            chat.last_message.connect(message)
            chat.save()
            
            # Return message details
            response_data = {
                'uid': message.uid,
                'text': message.text,
                'message_type': message.message_type,
                'created_at': str(message.created_at),
                'sender': {
                    'uid': user.uid,
                    'username': user.username,
                    'display_name': user.display_name
                },
                'feeling': {
                    'name': feeling_connected.name,
                    'color': feeling_connected.color
                } if feeling_connected else None,
                'message': 'Message sent successfully'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
