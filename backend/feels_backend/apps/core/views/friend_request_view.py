from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
import json
from datetime import datetime

from ..models import Account, FriendRequest
from ..authentication import authenticate_request


class FriendRequestView(APIView):
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
            action = data.get('action')  # 'accept', 'reject'
            
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
