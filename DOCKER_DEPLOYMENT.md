# 🐳 Docker Deployment Guide - AutoGrade+

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Set your API key
echo "GROQ_API_KEY=your_api_key_here" > .env

# 2. Build and run
docker-compose up -d

# 3. Access the application
# Open browser: http://localhost:5000
```

### Option 2: Docker Only

```bash
# 1. Build the image
docker build -t autograde-plus .

# 2. Run the container
docker run -d \
  -p 5000:5000 \
  -e GROQ_API_KEY=your_api_key_here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/lora_model:/app/lora_model \
  --name autograde-plus \
  autograde-plus

# 3. Access the application
# Open browser: http://localhost:5000
```

## Container Management

### View Logs
```bash
docker-compose logs -f
# or
docker logs -f autograde-plus
```

### Stop Container
```bash
docker-compose down
# or
docker stop autograde-plus
```

### Restart Container
```bash
docker-compose restart
# or
docker restart autograde-plus
```

### Remove Container
```bash
docker-compose down -v
# or
docker rm -f autograde-plus
```

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
FLASK_ENV=production
```

## Volume Mounts

The container uses the following volumes:

- `./data:/app/data` - Stores uploaded files and grading results
- `./lora_model:/app/lora_model` - LoRA model weights (if using fine-tuned model)

## Health Check

The container includes a health check that runs every 30 seconds:

```bash
# Check container health
docker ps

# Manual health check
curl http://localhost:5000/health
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs autograde-plus

# Common issues:
# 1. Port 5000 already in use
#    Solution: Change port in docker-compose.yml or stop other service

# 2. Missing API key
#    Solution: Add GROQ_API_KEY to .env file

# 3. Permission issues
#    Solution: Run with sudo or fix file permissions
```

### Can't access application
```bash
# Verify container is running
docker ps | grep autograde

# Check port mapping
docker port autograde-plus

# Test from inside container
docker exec -it autograde-plus curl http://localhost:5000
```

### Out of memory
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory

# Or limit container memory
docker run --memory="4g" ...
```

## Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml autograde

# Scale service
docker service scale autograde_autograde-plus=3
```

### Using Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autograde-plus
spec:
  replicas: 3
  selector:
    matchLabels:
      app: autograde-plus
  template:
    metadata:
      labels:
        app: autograde-plus
    spec:
      containers:
      - name: autograde-plus
        image: autograde-plus:latest
        ports:
        - containerPort: 5000
        env:
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: autograde-secrets
              key: groq-api-key
```

## Security Best Practices

1. **Never commit .env file** to version control
2. **Use secrets management** in production (e.g., Docker secrets, Kubernetes secrets)
3. **Run as non-root user** (already configured in Dockerfile)
4. **Keep base image updated** (`docker pull python:3.12-slim`)
5. **Scan for vulnerabilities** (`docker scan autograde-plus`)

## Performance Optimization

### Multi-stage Build
The Dockerfile uses multi-stage builds to reduce image size:
- Builder stage: Compiles dependencies
- Final stage: Only runtime files

### Image Size
```bash
# Check image size
docker images autograde-plus

# Expected size: ~500MB (Python + dependencies)
```

### Caching
```bash
# Build with cache
docker build -t autograde-plus .

# Build without cache (clean build)
docker build --no-cache -t autograde-plus .
```

## Monitoring

### Resource Usage
```bash
# Real-time stats
docker stats autograde-plus

# One-time stats
docker stats --no-stream autograde-plus
```

### Logs
```bash
# Follow logs
docker logs -f autograde-plus

# Last 100 lines
docker logs --tail 100 autograde-plus

# Since specific time
docker logs --since 2024-12-04T00:00:00 autograde-plus
```

## Backup and Restore

### Backup Data
```bash
# Backup uploaded files
docker cp autograde-plus:/app/data ./backup/data

# Backup LoRA model
docker cp autograde-plus:/app/lora_model ./backup/lora_model
```

### Restore Data
```bash
# Restore uploaded files
docker cp ./backup/data autograde-plus:/app/data

# Restore LoRA model
docker cp ./backup/lora_model autograde-plus:/app/lora_model
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: docker build -t autograde-plus .
    
    - name: Run tests
      run: docker run autograde-plus python -m pytest
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag autograde-plus username/autograde-plus:latest
        docker push username/autograde-plus:latest
```

## FAQ

**Q: Can I use this without Docker?**  
A: Yes, run `python chat_server.py` directly. Docker is optional but recommended.

**Q: How do I update the application?**  
A: Pull latest code, rebuild image: `docker-compose up -d --build`

**Q: Can I run multiple instances?**  
A: Yes, use different ports: `docker run -p 5001:5000 ...`

**Q: Does it work on ARM (Apple Silicon)?**  
A: Yes, Docker will automatically build for your architecture.

---

**Need help?** Open an issue or contact: i222371@nu.edu.pk
