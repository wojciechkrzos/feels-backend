from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
import json

from ..models import Feeling, FeelingType


class FeelingView(APIView):
    """API views for Feeling management"""
    
    @extend_schema(
        summary="List all feelings",
        description="Retrieve a list of all available feelings with their colors and types",
        responses={
            200: {
                "description": "List of feelings",
                "example": {
                    "feelings": [
                        {
                            "name": "Happy",
                            "color": "#FFD700",
                            "description": "A feeling of joy and contentment",
                            "feeling_type": "Positive"
                        },
                        {
                            "name": "Sad",
                            "color": "#4169E1", 
                            "description": "A feeling of sorrow or melancholy",
                            "feeling_type": "Negative"
                        }
                    ]
                }
            },
            500: {"description": "Internal server error"}
        }
    )
    def get(self, request):
        """List all feelings"""
        try:
            feelings = Feeling.nodes.all()
            return Response({
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
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Create a new feeling",
        description="Create a new feeling with name, color, and optional description and type",
        request={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the feeling"},
                "color": {"type": "string", "description": "Hex color code for the feeling"},
                "description": {"type": "string", "description": "Description of the feeling (optional)"},
                "feeling_type_name": {"type": "string", "description": "Name of the feeling type to associate with (optional)"}
            },
            "required": ["name", "color"],
            "example": {
                "name": "Excited",
                "color": "#FF6347",
                "description": "A feeling of enthusiasm and energy",
                "feeling_type_name": "Positive"
            }
        },
        responses={
            201: {
                "description": "Feeling created successfully",
                "example": {
                    "name": "Excited",
                    "color": "#FF6347",
                    "description": "A feeling of enthusiasm and energy",
                    "message": "Feeling created successfully"
                }
            },
            400: {"description": "Bad request - validation error"},
            500: {"description": "Internal server error"}
        }
    )
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
            
            return Response({
                'name': feeling.name,
                'message': 'Feeling created successfully'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
