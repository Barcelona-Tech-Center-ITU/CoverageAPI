# GIGA Coverage API

Open source backend services for the GIGA Coverage Library. This microservices architecture provides three main endpoints for mobile network coverage data collection.

## Architecture

### Services

1. **key-service** - Lightweight service for API key generation
   - Endpoint: `/api/get-key`
   - Resources: 256MB RAM
   - Purpose: Generate UUID-based API keys for device authentication

2. **data-service** - Data ingestion and storage service
   - Endpoint: `/api/send-data`
   - Resources: 512MB-1GB RAM
   - Purpose: Store coverage measurements in PostgreSQL
   - Database: PostgreSQL for persistent storage

3. **upload-service** - Upload speed testing service
   - Endpoint: `/api/test-upload`
   - Resources: 1-2GB RAM, high CPU
   - Purpose: Measure upload speeds without data persistence

### Technology Stack

- **FastAPI** - Python web framework
- **PostgreSQL** - Database for coverage data
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy and load balancer

## Quick Start

### Development Setup

```bash
# Clone and start services
cd "Coverage API"
docker-compose up -d

# API will be available at:
# http://localhost/api/get-key
# http://localhost/api/send-data  
# http://localhost/api/test-upload
```

### Production Setup

```bash
# Copy environment file and configure
cp .env.example .env
# Edit .env with your production values

# Start production stack
docker-compose -f docker-compose.prod.yml up -d
```

## API Endpoints

### 1. Get API Key
```bash
POST /api/get-key
Content-Type: application/json

{
  "android_id": "your-android-id"
}
```

Response:
```json
{
  "api_key": "uuid-based-key",
  "status": "success"
}
```

### 2. Send Coverage Data
```bash
POST /api/send-data
Content-Type: application/json

{
  "api_key": "your-api-key",
  "android_id": "your-android-id",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "signal_strength_dbm": -70,
  "network_type": "LTE",
  "download_speed_kbps": 1500
}
```

Response:
```json
{
  "status": "success",
  "message": "Coverage data stored successfully"
}
```

### 3. Test Upload Speed
```bash
POST /api/test-upload
Content-Type: multipart/form-data

api_key: your-api-key
file: [binary file data]
```

Response:
```json
{
  "upload_speed_mbps": 5.2,
  "upload_speed_kbps": 5324.8,
  "file_size_bytes": 1048576,
  "upload_time_seconds": 1.572,
  "status": "success"
}
```

## Health Checks

- `/health/key` - Key service health
- `/health/data` - Data service health  
- `/health/upload` - Upload service health
- `/stats` - Database statistics

## Development

### Local Development

```bash
# Start database only
docker-compose up postgres

# Install dependencies and run individual services
cd key-service && pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8001

cd data-service && pip install -r requirements.txt  
python -m uvicorn main:app --reload --port 8002

cd upload-service && pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8003
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U coverage -d coverage_db

# View statistics
SELECT * FROM coverage_stats;
SELECT * FROM network_type_distribution;
```

## Deployment Options

### VPS Deployment (Recommended)

1. **Requirements**: 4GB RAM, 2 CPU cores, 50GB storage
2. **Install Docker & Docker Compose**
3. **Clone repository and configure environment**
4. **Start with production compose file**

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml coverage-api
```

### Kubernetes

```bash
# Convert compose to K8s manifests
kompose convert -f docker-compose.prod.yml

# Deploy to cluster
kubectl apply -f .
```

## Monitoring & Maintenance

### Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service
docker-compose logs -f data-service
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U coverage coverage_db > backup.sql

# Restore backup  
docker-compose exec postgres psql -U coverage coverage_db < backup.sql
```

### Scaling Services

```bash
# Scale data service for high load
docker-compose up -d --scale data-service=3

# Scale upload service
docker-compose up -d --scale upload-service=2
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

### Resource Limits

Default resource allocation per service:
- **key-service**: 256MB RAM
- **data-service**: 1GB RAM  
- **upload-service**: 2GB RAM, 1 CPU core

Adjust in `docker-compose.yml` based on your server capacity.

## Security Considerations

- Change default PostgreSQL credentials in production
- Use SSL certificates for HTTPS (mount to `/etc/nginx/ssl`)
- Implement rate limiting if needed
- Consider API authentication beyond API keys for production

## Contributing

This is an open source project. Contributions welcome!

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## License

Open Source - MIT License