# Docker Best Practices for Python Applications

## Image Optimization

### Multi-stage Builds
Use multi-stage builds to separate build dependencies from runtime, reducing final image size by 50-70%.

### Base Image Selection
- `python:3.11-slim` - Recommended for most apps (150MB)
- `python:3.11-alpine` - Smallest (50MB) but may have compatibility issues with some packages
- `python:3.11` - Full image (900MB), use only if you need build tools

### Layer Caching
Order Dockerfile instructions from least to most frequently changing:
1. System packages
2. requirements.txt (changes infrequently)
3. Application code (changes frequently)

## Security

### Non-root User
Always run containers as non-root:
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### Minimal Dependencies
- Use `--no-cache-dir` with pip to reduce image size
- Pin dependency versions in requirements.txt
- Scan images with `docker scan` or Trivy

### Secrets Management
Never hardcode secrets. Use:
- Environment variables
- Docker secrets (Swarm)
- Kubernetes secrets
- External secret managers (AWS Secrets Manager, HashiCorp Vault)

## Production Considerations

### Health Checks
Add health checks to Dockerfile:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"
```

### Logging
- Log to stdout/stderr (Docker handles collection)
- Use structured logging (JSON) for parsing
- Configure log drivers in docker-compose.yml

### Resource Limits
Set memory and CPU limits:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

## Common Patterns

### Web Applications
```dockerfile
EXPOSE 8000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
```

### Background Workers
```dockerfile
CMD ["python", "-u", "worker.py"]  # -u for unbuffered output
```

### CLI Tools
```dockerfile
ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]
```

## Networking

### Port Mapping
- EXPOSE in Dockerfile documents the port
- Bind with `-p` or `ports:` in compose
- Use host networking sparingly (`network_mode: host`)

### Service Discovery
In docker-compose, services can reach each other by service name:
```python
import requests
response = requests.get('http://database:5432')
```

## Troubleshooting

### Debugging
```bash
# Run with shell
docker run -it --entrypoint /bin/sh my-app

# View logs
docker logs -f container_name

# Inspect container
docker inspect container_name

# Execute command in running container
docker exec -it container_name python
```

### Common Issues
- **Permission denied**: Check file ownership and USER directive
- **Module not found**: Ensure requirements.txt is complete
- **Connection refused**: Check EXPOSE and port mappings
- **Large image size**: Use multi-stage builds and .dockerignore
