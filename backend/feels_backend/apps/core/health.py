from rest_framework.views import APIView
from rest_framework.response import Response
from neomodel import db
import time
from drf_spectacular.utils import extend_schema

class HealthCheckView(APIView):
    @extend_schema(
        summary="Health Check",
        description="Check the health status of the API and its dependencies",
        responses={
            200: {
                "description": "Service is healthy",
                "example": {
                    "status": "healthy",
                    "timestamp": 1640995200.0,
                    "services": {
                        "neo4j": {"status": "healthy", "response_time_ms": 12.34},
                        "django": {"status": "healthy", "version": "5.2"}
                    }
                }
            },
            503: {
                "description": "Service is unhealthy",
                "example": {
                    "status": "unhealthy",
                    "timestamp": 1640995200.0,
                    "services": {
                        "neo4j": {"status": "unhealthy", "error": "Connection failed"},
                        "django": {"status": "healthy", "version": "5.2"}
                    }
                }
            }
        }
    )
    def get(self, request):
        """Health check endpoint"""
        
        start_time = time.time()
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {}
        }
        
        # Check Neo4j connection
        try:
            result = db.cypher_query("RETURN 1 as test")
            health_status["services"]["neo4j"] = {
                "status": "healthy",
                "response_time_ms": round((time.time() - start_time) * 1000, 2)
            }
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["services"]["neo4j"] = {
                "status": "unhealthy", 
                "error": str(e)
            }
        
        # Check Django
        health_status["services"]["django"] = {
            "status": "healthy",
            "version": "5.2"
        }
        
        return Response(health_status, status=200 if health_status["status"] == "healthy" else 503)
