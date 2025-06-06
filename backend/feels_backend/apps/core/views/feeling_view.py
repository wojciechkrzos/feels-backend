from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
import json

from ..models import Feeling, FeelingType


class FeelingView(APIView):
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
