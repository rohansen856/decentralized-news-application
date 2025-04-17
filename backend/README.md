# Load Balanced Backend Services

This directory contains a production-ready, load-balanced backend implementation with both Flask and FastAPI services for the decentralized news application.

## Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │────│    Nginx    │────│  Flask App  │
│ Application │    │Load Balancer│    │   (5000)    │
└─────────────┘    │             │    └─────────────┘
                   │             │    
                   │             │    ┌─────────────┐
                   │             │────│ FastAPI App │
                   │             │    │   (8000)    │
                   └─────────────┘    └─────────────┘
                           │
                   ┌───────┼───────┐
                   │       │       │
            ┌──────────┐ ┌──────┐ ┌─────────┐
            │PostgreSQL│ │Redis │ │ MongoDB │
            │  (5432)  │ │(6379)│ │ (27017) │
            └──────────┘ └──────┘ └─────────┘
```

## Services

### 🌐 **Nginx Load Balancer (Port 80)**
- Routes traffic between Flask and FastAPI backends
- Implements rate limiting and security headers
- Health checks and error handling
- Optimized for high performance

### 🐍 **Flask Backend (Port 5000)**
- Authentication and user management
- Session-based operations
- Traditional web framework approach
- Handles: `/api/v1/auth`, `/api/v1/users`, `/api/v1/analytics`

### ⚡ **FastAPI Backend (Port 8000)**
- High-performance async operations
- ML-powered recommendations
- Database-heavy operations
- Handles: `/api/v1/articles`, `/api/v1/interactions`, `/api/v1/recommendations`, `/api/v1/search`

### 🗄️ **Database Services**
- **PostgreSQL**: Relational data, user info, articles
- **MongoDB**: Document storage, flexible schemas
- **Redis**: Caching, session storage, real-time data

## Quick Start

### 1. Environment Setup
```bash
# Copy and configure environment variables
cp .env.example .env
nano .env  # Configure your settings
```

### 2. Start All Services
```bash
# Start complete backend stack
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
curl http://localhost/api/v1/health
```

### 3. Initialize Database
```bash
# Run database setup (from project root)
cd database && ./setup_databases.sh
```

## API Endpoints

### Authentication (Flask)
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh token

### Users (Flask)
- `GET /api/v1/users` - List users (admin)
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Articles (FastAPI)
- `GET /api/v1/articles` - List articles with filtering
- `GET /api/v1/articles/{id}` - Get article details
- `POST /api/v1/articles` - Create article
- `PUT /api/v1/articles/{id}` - Update article
- `DELETE /api/v1/articles/{id}` - Delete article

### Interactions (FastAPI)
- `POST /api/v1/interactions` - Record user interaction
- `GET /api/v1/interactions/user/{id}` - Get user interactions

### Recommendations (FastAPI)
- `POST /api/v1/recommendations` - Get personalized recommendations

### Search (FastAPI)
- `POST /api/v1/search` - Full-text search articles

### Analytics (Flask)
- `POST /api/v1/analytics/user/{id}` - User analytics
- `POST /api/v1/analytics/article/{id}` - Article analytics

### Health Checks
- `GET /api/v1/health` - Service health status
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

## Load Balancing Strategy

### Route Distribution
- **Authentication & Users** → Flask (session management)
- **Articles & Search** → FastAPI (async performance)
- **Recommendations** → FastAPI (ML operations)
- **Analytics** → Flask (reporting)

### Features
- **Rate Limiting**: 10 req/s general, 5 req/s auth
- **Health Checks**: Automatic failover
- **Sticky Sessions**: For authentication if needed
- **Caching**: Redis-based response caching
- **Security**: CORS, headers, input validation

## Development

### Running Individual Services
```bash
# Flask development server
cd flask_app && python app.py

# FastAPI development server
cd fastapi_app && uvicorn main:app --reload

# Start only databases
docker-compose up postgres mongodb redis -d
```

### Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Load testing
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"testpass123"}'
```

### Monitoring
```bash
# Start with monitoring
docker-compose --profile monitoring up -d

# Access Prometheus
open http://localhost:9090

# Check nginx status
curl http://localhost:8080/nginx-health
```

## Production Deployment

### Environment Variables
```env
# Security
JWT_SECRET_KEY=your-super-secret-production-key
BCRYPT_ROUNDS=12

# Database passwords
POSTGRES_PASSWORD=secure-password
MONGODB_PASSWORD=secure-password
REDIS_PASSWORD=secure-password

# Performance
WORKERS=4
MAX_CONNECTIONS=100
```

### SSL Configuration
1. Obtain SSL certificates
2. Update `nginx/nginx.conf` with HTTPS configuration
3. Restart services

### Scaling
```bash
# Scale Flask instances
docker-compose up --scale flask_app=3 -d

# Scale FastAPI instances
docker-compose up --scale fastapi_app=3 -d
```

## Troubleshooting

### Common Issues
```bash
# Check service logs
docker-compose logs flask_app
docker-compose logs fastapi_app
docker-compose logs nginx

# Database connection issues
docker-compose exec postgres psql -U postgres -d news_app
docker-compose exec mongodb mongosh

# Reset services
docker-compose down && docker-compose up -d
```

### Performance Tuning
- Adjust worker processes in nginx.conf
- Configure database connection pools
- Optimize Redis memory settings
- Enable gzip compression

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Rate limiting and DDoS protection
- Input validation and sanitization
- SQL injection prevention
- CORS configuration
- Security headers
- Non-root container users

## Monitoring & Observability

- Health check endpoints
- Prometheus metrics integration
- Request/response timing
- Error logging and tracking
- Database connection monitoring
- Cache hit/miss rates

---

**🚀 Your load-balanced backend is ready for production!**

Access the API documentation:
- **Swagger UI**: http://localhost/api/v1/docs (FastAPI)
- **Health Check**: http://localhost/api/v1/health