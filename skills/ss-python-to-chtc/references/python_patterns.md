# Python Application Patterns for Docker

## Application Types

### Script Applications
Simple single-file scripts that run and exit:
```dockerfile
CMD ["python", "script.py"]
```

### Long-running Services
Web servers, APIs, or daemons:
```dockerfile
CMD ["gunicorn", "app:app", "--workers", "4"]
```

### Worker Processes
Background task processors (Celery, RQ):
```dockerfile
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
```

### Scheduled Jobs
Cron-like periodic tasks:
```dockerfile
CMD ["python", "-c", "import schedule; schedule.every().hour.do(job); schedule.run_pending()"]
```

## Common Dependencies

### Web Frameworks
- **Flask**: lightweight, use with gunicorn/uwsgi
- **FastAPI**: modern async, use with uvicorn
- **Django**: full-featured, use with gunicorn

### Data Processing
- **pandas**: Data manipulation (requires compilation)
- **numpy**: Numerical computing (use appropriate base image)
- **scikit-learn**: Machine learning (large image)

### Database Clients
- **psycopg2-binary**: PostgreSQL (use binary for Docker)
- **pymongo**: MongoDB
- **redis**: Redis client

## Dependency Management

### requirements.txt Format
```txt
# Production dependencies
flask==2.3.0
gunicorn==20.1.0
psycopg2-binary==2.9.6

# Optional: Development dependencies
# pytest==7.3.1
# black==23.3.0
```

### Version Pinning Strategies
- **Exact pins** (`==`): Maximum reproducibility, manual updates
- **Compatible release** (`~=`): Patch updates only
- **Minimum version** (`>=`): Flexible but risky

### Handling C Extensions
Some packages require compilation:
- Use `-slim` base image and install build dependencies
- Or use pre-built binary wheels (`-binary` suffix)
- Or use `alpine` with appropriate dev packages

## Environment Configuration

### Environment Variables
```python
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///default.db')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
PORT = int(os.environ.get('PORT', 8000))
```

### Config Files
Mount configuration files as volumes:
```yaml
volumes:
  - ./config.yaml:/app/config.yaml:ro
```

### Python-dotenv
Load from .env file (dev) or environment (prod):
```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file if present
```

## File System Considerations

### Write Permissions
Container filesystem is typically read-only. For writes:
- Use volumes: `-v ./data:/app/data`
- Use tmpfs: `--tmpfs /tmp`
- Or run as root (not recommended)

### File Uploads
Store uploaded files in volumes, not container filesystem:
```python
UPLOAD_FOLDER = '/app/uploads'  # Mount as volume
```

### Static Files
For web apps, serve static files:
- Through web server (nginx)
- Or using WhiteNoise (Python)
- Or from CDN

## Signal Handling

### Graceful Shutdown
Handle SIGTERM for clean shutdown:
```python
import signal
import sys

def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    # Cleanup code here
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
```

### PID 1 Problem
Use `exec` form of CMD to avoid shell wrapper:
```dockerfile
# Good: Process gets SIGTERM
CMD ["python", "app.py"]

# Bad: Shell gets SIGTERM, not python
CMD python app.py
```

Or use tini as init process:
```dockerfile
RUN apt-get update && apt-get install -y tini
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "app.py"]
```
