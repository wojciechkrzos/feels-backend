from django.http import JsonResponse
from django.views import View
from neomodel import db
import time

class HealthCheckView(View):
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
        
        return JsonResponse(health_status, status=200 if health_status["status"] == "healthy" else 503)
