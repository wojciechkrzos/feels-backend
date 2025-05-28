# 🐳 Neo4j Container Management Guide

## Quick Start Commands

### 1. Check Container Status
```bash
sudo docker ps -a | grep neo4j
```

### 2. Start Neo4j (if stopped)
```bash
sudo docker start neo4j-feels
```

### 3. Stop Neo4j
```bash
sudo docker stop neo4j-feels
```

### 4. Restart Neo4j
```bash
sudo docker restart neo4j-feels
```

### 5. View Logs
```bash
sudo docker logs neo4j-feels --tail 20
```

## Create New Neo4j Container

If you need to create a fresh container:

```bash
# Remove existing container (if needed)
sudo docker stop neo4j-feels
sudo docker rm neo4j-feels

# Create new container
sudo docker run -d \
    --name neo4j-feels \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -v neo4j-data:/data \
    neo4j:latest
```

## Access Neo4j

### Web Interface
- **URL**: http://localhost:7474
- **Username**: neo4j
- **Password**: password

### Connection String (for Django)
```
bolt://neo4j:password@localhost:7687
```

## Django Integration

### Test Connection
```bash
cd feels_backend
source ../venv/bin/activate
python manage.py shell -c "
from neomodel import db
result = db.cypher_query('RETURN 1 as test')
print('Neo4j connection successful:', result)
"
```

### Install Schema
```bash
python manage.py install_labels
```

### Populate Sample Data
```bash
python manage.py populate_db
```

### Check Health
```bash
curl http://localhost:8002/api/health/
```

## Troubleshooting

### Container Won't Start
```bash
# Check if port is already in use
sudo netstat -tlnp | grep :7474
sudo netstat -tlnp | grep :7687

# Check container logs
sudo docker logs neo4j-feels
```

### Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Then logout and login again
```

### Connection Refused
```bash
# Wait for Neo4j to fully start (may take 10-30 seconds)
sleep 15

# Check if Neo4j is accepting connections
curl http://localhost:7474/
```

## Production Notes

For production use:
- Change the default password
- Use environment variables for credentials
- Set up proper volumes for data persistence
- Configure memory settings
- Enable SSL/TLS
