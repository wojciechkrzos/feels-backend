"""
Test configuration module
Loads environment variables for test scripts
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / '.env')

# Configuration constants
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
DJANGO_PORT = int(os.getenv('DJANGO_PORT', '8000'))
NEO4J_HOST = os.getenv('NEO4J_HOST', 'localhost')
NEO4J_PORT = int(os.getenv('NEO4J_PORT', '7687'))
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

# For backwards compatibility
BASE_URL = API_BASE_URL
