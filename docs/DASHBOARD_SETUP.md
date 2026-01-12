# Dashboard Setup Guide

## Overview

This guide covers deploying the real-time web dashboard for monitoring benchmark progress.

## Quick Start

### Development Mode

```bash
# Install dependencies
pip install flask flask-cors plotly

# Start dashboard
python dashboard/app.py

# Open browser
open http://localhost:8080
```

### Production Mode

```bash
# Use production WSGI server
pip install gunicorn

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 dashboard.app:app
```

## Features

### Available Pages

1. **Overview Dashboard** (`/`)
   - Current iteration progress
   - Phase indicator
   - Live accuracy gauge
   - Worker status grid

2. **Metrics Dashboard** (`/metrics`)
   - Real-time charts
   - Accuracy trends
   - Latency percentiles
   - Throughput history

3. **Leaderboard** (`/leaderboard`)
   - Agent rankings
   - Win rates
   - Performance comparison

4. **System Health** (`/health`)
   - GPU temperatures
   - Memory usage
   - Disk I/O

### API Endpoints

```
GET /api/status          - System status
GET /api/benchmarks      - Recent benchmarks
GET /api/latest          - Latest benchmark result
GET /api/iterations      - Iteration history
GET /api/workers         - Worker status
```

## Configuration

### Environment Variables

```bash
# .env file
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
FLASK_DEBUG=false

DATABASE_PATH=dashboard/benchmark_data.db
BENCHMARK_DIR=logs/benchmarks
CHECKPOINT_DIR=checkpoints

# WebSocket settings
WEBSOCKET_ENABLED=true
WEBSOCKET_PORT=8081

# Authentication (optional)
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=secure_password
```

### Configuration File

```yaml
# config/dashboard_config.yaml
dashboard:
  host: "0.0.0.0"
  port: 8080
  debug: false
  
  database:
    type: "sqlite"
    path: "dashboard/benchmark_data.db"
  
  websocket:
    enabled: true
    port: 8081
  
  update_interval: 1  # seconds
  
  auth:
    enabled: false
    username: "${DASHBOARD_USERNAME}"
    password: "${DASHBOARD_PASSWORD}"
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY dashboard/ ./dashboard/
COPY config/ ./config/
COPY logs/ ./logs/

# Expose port
EXPOSE 8080

# Run dashboard
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "dashboard.app:app"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    volumes:
      - ./logs:/app/logs
      - ./checkpoints:/app/checkpoints
      - ./dashboard/benchmark_data.db:/app/dashboard/benchmark_data.db
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
  
  websocket:
    build:
      context: .
      dockerfile: Dockerfile.websocket
    ports:
      - "8081:8081"
    depends_on:
      - dashboard
    restart: unless-stopped
```

### Running with Docker

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## SSL/TLS Configuration

### Using Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/dashboard
server {
    listen 443 ssl http2;
    server_name dashboard.evolving-sun.ai;
    
    ssl_certificate /etc/letsencrypt/live/dashboard.evolving-sun.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dashboard.evolving-sun.ai/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws {
        proxy_pass http://localhost:8081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Obtaining SSL Certificate

```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d dashboard.evolving-sun.ai

# Auto-renewal
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet
```

## Firewall Configuration

### UFW (Ubuntu)

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow dashboard (if not using reverse proxy)
sudo ufw allow 8080/tcp

# Allow WebSocket
sudo ufw allow 8081/tcp

# Enable firewall
sudo ufw enable
```

### iptables

```bash
# Allow dashboard
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# Allow WebSocket
sudo iptables -A INPUT -p tcp --dport 8081 -j ACCEPT

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

## Access Control

### Basic Authentication

```python
# dashboard/auth.py
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    """Check if username/password is valid."""
    return (username == os.getenv('DASHBOARD_USERNAME') and
            password == os.getenv('DASHBOARD_PASSWORD'))

def authenticate():
    """Send 401 response."""
    return Response(
        'Authentication required',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Usage
@app.route('/')
@requires_auth
def index():
    return render_template('index.html')
```

### IP Whitelist

```python
# dashboard/app.py
ALLOWED_IPS = ['10.0.0.0/8', '192.168.0.0/16']

@app.before_request
def limit_remote_addr():
    client_ip = request.remote_addr
    if not any(ipaddress.ip_address(client_ip) in ipaddress.ip_network(net) 
               for net in ALLOWED_IPS):
        abort(403)
```

## Monitoring Dashboard Health

### Health Check Endpoint

```python
@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - app.start_time,
        'database': check_database_connection(),
        'disk_space': check_disk_space()
    })
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest

request_counter = Counter('dashboard_requests_total', 'Total requests')
request_duration = Histogram('dashboard_request_duration_seconds', 'Request duration')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_duration.observe(time.time() - request.start_time)
    request_counter.inc()
    return response

@app.route('/metrics')
def metrics():
    return generate_latest()
```

## Performance Optimization

### Caching

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

@app.route('/api/benchmarks')
@cache.cached(timeout=60)
def api_benchmarks():
    # Cached for 60 seconds
    return jsonify(get_benchmarks())
```

### Database Optimization

```sql
-- Create indexes for faster queries
CREATE INDEX idx_iterations_timestamp ON iterations(timestamp);
CREATE INDEX idx_iterations_benchmark ON iterations(benchmark_name);
CREATE INDEX idx_benchmarks_started ON benchmarks(started_at);
```

### Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///benchmark_data.db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

## Troubleshooting

### Dashboard Not Accessible

```bash
# Check if process is running
ps aux | grep dashboard

# Check port binding
netstat -tulpn | grep 8080

# Check firewall
sudo ufw status
```

### WebSocket Connection Failed

```bash
# Check WebSocket server
ps aux | grep websocket

# Test connection
wscat -c ws://localhost:8081
```

### Slow Performance

```bash
# Enable debug mode
export FLASK_DEBUG=1

# Profile requests
pip install flask-profiler
```

### Database Lock Errors

```python
# Use WAL mode for SQLite
import sqlite3
conn = sqlite3.connect('benchmark_data.db')
conn.execute('PRAGMA journal_mode=WAL')
```

## Backup and Recovery

### Database Backup

```bash
# Backup SQLite database
sqlite3 dashboard/benchmark_data.db ".backup 'backup/db_$(date +%Y%m%d).db'"

# Automated backups (cron)
0 0 * * * sqlite3 /app/dashboard/benchmark_data.db ".backup '/backups/db_$(date +\%Y\%m\%d).db'"
```

### Restore Database

```bash
# Restore from backup
cp backup/db_20260112.db dashboard/benchmark_data.db
```

## Maintenance

### Log Rotation

```bash
# /etc/logrotate.d/dashboard
/app/logs/dashboard/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Cleanup Old Data

```python
# cleanup_old_data.py
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('dashboard/benchmark_data.db')

# Delete iterations older than 30 days
cutoff = datetime.now() - timedelta(days=30)
conn.execute('DELETE FROM iterations WHERE timestamp < ?', (cutoff.timestamp(),))
conn.commit()
```

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
