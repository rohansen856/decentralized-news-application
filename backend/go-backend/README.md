# News App Go Backend

A robust Go backend service for the decentralized news application, built with Gin framework and supporting PostgreSQL, MongoDB, and Redis.

## Features

- **RESTful API** with Gin framework
- **Multi-database support** (PostgreSQL, MongoDB, Redis)
- **JWT Authentication** with role-based access control
- **Input validation** with comprehensive error handling
- **CORS support** for cross-origin requests
- **Health checks** for all services
- **Docker support** with multi-stage builds
- **Graceful shutdown** handling
- **Structured logging** middleware

## Architecture

```
├── cmd/server/          # Application entry point
├── internal/
│   ├── auth/           # JWT authentication logic
│   ├── config/         # Configuration management
│   ├── database/       # Database connections & managers
│   ├── handlers/       # HTTP request handlers
│   ├── middleware/     # HTTP middleware
│   ├── models/         # Data models and schemas
│   └── utils/          # Utility functions
├── pkg/
│   ├── response/       # HTTP response helpers
│   └── validation/     # Input validation utilities
└── docs/               # API documentation
```

## Quick Start

### Prerequisites

- Go 1.22 or higher
- PostgreSQL
- MongoDB (optional)
- Redis (optional)

### Installation

1. Clone and navigate to the directory:
```bash
cd backend/go-backend
```

2. Copy environment file and configure:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Install dependencies:
```bash
go mod download
```

4. Run the application:
```bash
go run cmd/server/main.go
```

The server will start on `http://localhost:8080`

## Configuration

All configuration is managed through environment variables. See `.env.example` for all available options.

### Key Configuration Sections:

- **Server**: Port, host, timeouts
- **Database**: PostgreSQL connection settings
- **Auth**: JWT secrets and expiry times
- **Redis**: Caching configuration
- **MongoDB**: Document storage settings

## API Endpoints

### Health Check
- `GET /api/v1/health` - Service health status

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/profile` - Get user profile (requires auth)

### User Roles
- `reader` - Can read articles
- `author` - Can read and write articles
- `administrator` - Full access
- `auditor` - Can audit content

## Database Schema

The service uses PostgreSQL as the primary database with support for:
- Users with role-based access
- Articles with rich metadata
- User interactions and analytics
- JSON fields for flexible data storage

## Development

### Using Make Commands

```bash
# Setup development environment
make setup

# Run with live reload (requires air)
make dev

# Run tests
make test

# Build application
make build

# Format code
make fmt

# Run linter
make lint
```

### Docker Development

```bash
# Build Docker image
make docker-build

# Run container
make docker-run

# Use docker-compose
make docker-compose-up
```

## Authentication

The service uses JWT tokens for authentication:

1. Register/login to receive a JWT token
2. Include token in Authorization header: `Bearer <token>`
3. Tokens expire after 24 hours (configurable)

## Error Handling

All API responses follow a consistent format:

**Success Response:**
```json
{
  "success": true,
  "message": "Operation successful",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {...}
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {...},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Security Features

- Password hashing with bcrypt
- JWT token validation
- Role-based access control
- CORS protection
- SQL injection prevention
- Input validation and sanitization

## Monitoring

The `/api/v1/health` endpoint provides:
- Service status
- Database connectivity
- Version information
- Individual service health

## Contributing

1. Follow Go coding standards
2. Add tests for new features
3. Update documentation
4. Use conventional commit messages

## License

This project is part of the decentralized news application.