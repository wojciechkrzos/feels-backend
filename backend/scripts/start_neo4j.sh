#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Set defaults if not provided
NEO4J_USER=${NEO4J_USER:-neo4j}
NEO4J_PASSWORD=${NEO4J_PASSWORD:-password}
NEO4J_PORT=${NEO4J_PORT:-7687}

echo "🚀 Starting Neo4j container for Feels Backend..."

# Check if container already exists
if sudo docker ps -a | grep -q neo4j-feels; then
    echo "📦 Neo4j container already exists. Starting it..."
    sudo docker start neo4j-feels
else
    echo "📦 Creating new Neo4j container..."
    sudo docker run -d \
        --name neo4j-feels \
        -p 7474:7474 \
        -p ${NEO4J_PORT}:7687 \
        -e NEO4J_AUTH=${NEO4J_USER}/${NEO4J_PASSWORD} \
        -v neo4j-data:/data \
        neo4j:latest
fi

echo "⏳ Waiting for Neo4j to start..."
sleep 10

# Check if Neo4j is running
if sudo docker ps | grep -q neo4j-feels; then
    echo "✅ Neo4j is running successfully!"
    echo "🌐 Web interface: http://localhost:7474"
    echo "🔌 Bolt connection: bolt://localhost:${NEO4J_PORT}"
    echo "🔑 Credentials: ${NEO4J_USER}/${NEO4J_PASSWORD}"
else
    echo "❌ Failed to start Neo4j container"
    exit 1
fi
