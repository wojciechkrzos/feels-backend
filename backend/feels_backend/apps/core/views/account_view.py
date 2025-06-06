from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

from ..models import Account
from ..authentication import hash_password


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
                pass
            
            # Check if email already exists
            try:
                Account.nodes.get(email=data['email'])
                return JsonResponse({'error': 'Email already exists'}, status=400)
            except Account.DoesNotExist:
                pass
            
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
