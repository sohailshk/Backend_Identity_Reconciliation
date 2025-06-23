# Contact Reconciliation Service

[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions/workflows/ci-cd.yml)
[![Docker Image](https://img.shields.io/docker/v/YOUR_DOCKER_USERNAME/contact-reconciliation-api?label=docker&logo=docker)](https://hub.docker.com/r/YOUR_DOCKER_USERNAME/contact-reconciliation-api)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A FastAPI-based backend service for managing contacts and identifying relationships between them based on shared email addresses or phone numbers.

## Project Structure

```
project/
├── app/
│   ├── main.py          # FastAPI application and routes
│   ├── models.py        # SQLAlchemy database models
│   ├── database.py      # Database configuration and session management
│   ├── schemas.py       # Pydantic schemas for request/response validation
│   └── init_db.py       # Database initialization script
├── tests/
│   ├── __init__.py      # Tests package init
│   ├── conftest.py      # Pytest configuration
│   └── test_identify.py # Comprehensive test suite
├── data/                # SQLite database persistence (created by Docker)
├── Dockerfile           # Multi-stage Docker container definition
├── docker-compose.yml   # Docker Compose configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Features

- **Contact Management**: Create, read, update, and delete contacts
- **Advanced Contact Reconciliation**: Identify and merge related contacts with complex logic
- **Contact Group Merging**: Automatically merge overlapping contact groups under earliest primary
- **SQLite Database**: Local database with SQLAlchemy ORM and optimized indexes
- **Input Validation**: Email and phone number format validation
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Health Check**: Service health monitoring endpoint
- **Comprehensive Testing**: Full test suite with pytest
- **Error Handling**: Robust error handling with security-conscious responses
- **Docker Support**: Fully containerized with multi-stage builds and health checks
- **Database Persistence**: SQLite database persisted across container restarts

## Database Schema

### Contact Model
- `id`: Integer, Primary Key (indexed)
- `phoneNumber`: String (nullable, indexed)
- `email`: String (nullable, indexed)
- `linkedId`: Integer (nullable, foreign key to Contact.id, indexed)
- `linkPrecedence`: Enum ("primary", "secondary", indexed)
- `createdAt`: DateTime (indexed)
- `updatedAt`: DateTime
- `deletedAt`: DateTime (nullable, indexed) - for soft deletion

### Database Optimizations
- Indexes on all searchable fields: `email`, `phoneNumber`, `linkedId`, `linkPrecedence`, `createdAt`, `deletedAt`
- Atomic transactions for all reconciliation operations
- Bulk updates for merging operations

## Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   ```bash
   cd app
   python init_db.py
   ```

3. **Run the Application**
   ```bash
   cd app
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Contact Reconciliation Logic

### Endpoint Behavior

The `/identify` endpoint implements sophisticated contact reconciliation:

1. **New Contact Creation**: If no matching contacts exist, creates a new primary contact
2. **Secondary Linking**: Links contacts with shared email/phone to existing primaries
3. **Group Merging**: When multiple primary contacts share relationships through secondaries, merges them under the earliest created primary
4. **Duplicate Prevention**: Prevents creation of exact duplicate contacts

### Merging Logic Summary

When the system detects overlapping contact groups (multiple primaries connected through shared secondaries):

1. **Identify the Winner**: The earliest created primary contact becomes the winning primary
2. **Demote Losers**: All other primary contacts are demoted to secondary status
3. **Relink Relationships**: All secondary contacts are relinked to point to the winning primary
4. **Atomic Updates**: All changes occur within a single database transaction

### Error Response Examples

```json
// Missing required fields
{
  "detail": "At least one of email or phoneNumber must be provided"
}

// Invalid email format
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error"
    }
  ]
}

// Server error (hides implementation details)
{
  "detail": "Service temporarily overloaded"
}
```

### Health Check
- `GET /health` - Returns service health status

### Contact Management
- `GET /` - Root endpoint with service information
- `POST /contacts` - Create a new contact
- `GET /contacts` - Get list of contacts (with pagination)
- `GET /contacts/{contact_id}` - Get specific contact by ID
- `PUT /contacts/{contact_id}` - Update existing contact
- `DELETE /contacts/{contact_id}` - Soft delete contact

### Contact Reconciliation
- `POST /identify` - Identify and reconcile contacts based on email/phone

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Contact
```bash
curl -X POST "http://localhost:8000/contacts" \
     -H "Content-Type: application/json" \
     -d '{"email": "john@example.com", "phoneNumber": "+1234567890"}'
```

### Get All Contacts
```bash
curl http://localhost:8000/contacts
```

### Get Specific Contact
```bash
curl http://localhost:8000/contacts/1
```

### Contact Reconciliation - Identify
```bash
# New contact
curl -X POST "http://localhost:8000/identify" \
     -H "Content-Type: application/json" \
     -d '{"email": "john@example.com", "phoneNumber": "+1234567890"}'

# Link existing contact
curl -X POST "http://localhost:8000/identify" \
     -H "Content-Type: application/json" \
     -d '{"email": "john@example.com", "phoneNumber": "+0987654321"}'

# Email only
curl -X POST "http://localhost:8000/identify" \
     -H "Content-Type: application/json" \
     -d '{"email": "john@example.com"}'
```

## Testing

Run the comprehensive test suite:

```bash
# Install testing dependencies (if not already installed)
pip install pytest pytest-cov pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_identify.py -v
```

### Test Coverage

The test suite covers:
- ✅ New contact creation
- ✅ Simple secondary contact linking  
- ✅ Complex primary contact merging
- ✅ Email-only and phone-only identification
- ✅ Input validation and error handling
- ✅ Duplicate prevention
- ✅ Complex multi-group merging scenarios

## Docker & Local Container Setup

The service is fully containerized using Docker for easy deployment and testing.

### Prerequisites

- **Docker Desktop**: Ensure Docker Desktop is installed and running
- **Docker Compose**: Included with Docker Desktop

### Quick Start with Docker

1. **Build and Start the Service**
   ```bash
   # Build and run in detached mode
   docker-compose up --build -d
   ```

2. **Verify Service Health**
   ```bash
   # Check if container is running
   docker ps
   
   # Test health endpoint
   curl http://localhost:8000/health
   # Expected response: {"status": "ok"}
   ```

3. **Test Contact Reconciliation**
   ```bash
   # Create a new contact
   curl -X POST "http://localhost:8000/identify" \
        -H "Content-Type: application/json" \
        -d '{"email": "test@example.com", "phoneNumber": "+1234567890"}'
   ```

### Docker Architecture

**Multi-stage Dockerfile:**
- **Builder Stage**: Installs dependencies with build tools (gcc)
- **Runtime Stage**: Minimal image with only runtime dependencies
- **Health Check**: Built-in curl-based health monitoring
- **Database Initialization**: Automatically creates tables on startup

**Docker Compose Features:**
- **Port Mapping**: Host port 8000 → Container port 8000
- **Volume Persistence**: SQLite database persisted in `./data/contacts.db`
- **Environment Variables**: Configurable database path
- **Health Monitoring**: Container health checks every 30 seconds
- **Auto-restart**: Service restarts unless manually stopped

### Container Management

```bash
# View running containers
docker ps

# View container logs
docker-compose logs -f contact-api

# Stop the service
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Rebuild and restart
docker-compose up --build -d

# Execute commands inside container
docker-compose exec contact-api bash
```

### Database Persistence

- **Location**: Database created inside container at `/app/app/contacts.db`
- **Access**: Database accessible through API endpoints
- **Persistence**: Data survives container restarts (can be enhanced with volume mounts)
- **Environment**: Uses `DATABASE_URL=sqlite:///contacts.db`

### Accessing the API

Once running, the API is available at:
- **Base URL**: `http://localhost:8000`
- **Health Check**: `http://localhost:8000/health`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc`

### Container Health Status

The container includes built-in health monitoring:
```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' $(docker-compose ps -q contact-api)

# View health check logs
docker inspect $(docker-compose ps -q contact-api) | grep -A 10 Health
```

## CI/CD Pipeline

This project includes a comprehensive GitHub Actions CI/CD pipeline that:

### Automated Testing (`build-and-test` job)
- Runs on every push and pull request to `main` and `develop` branches
- Tests against Python 3.11
- Runs full pytest suite with coverage reporting
- Performs code linting with flake8
- Uploads coverage reports to Codecov

### Docker Build & Deployment (`docker-build-and-push` job)
- Triggers on version tags (e.g., `v1.0.0`)
- Builds multi-platform Docker images (linux/amd64, linux/arm64)
- Pushes to Docker Hub with version tag and `latest`
- Creates GitHub releases automatically
- Uses Docker layer caching for faster builds

### Security Scanning (`security-scan` job)
- Runs on pushes to `main` branch
- Performs dependency vulnerability scanning with `safety`
- Runs static security analysis with `bandit`
- Uploads scan results as artifacts

### Setup Instructions

1. **Fork the repository** and clone it to your GitHub account

2. **Add Docker Hub secrets** to your GitHub repository:
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add the following repository secrets:
     - `DOCKER_USERNAME`: Your Docker Hub username
     - `DOCKER_PASSWORD`: Your Docker Hub access token

3. **Update badge URLs** in README.md:
   ```markdown
   # Replace YOUR_USERNAME and YOUR_REPO_NAME with actual values
   [![CI/CD Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions/workflows/ci-cd.yml/badge.svg)]
   
   # Replace YOUR_DOCKER_USERNAME with your Docker Hub username
   [![Docker Image](https://img.shields.io/docker/v/YOUR_DOCKER_USERNAME/contact-reconciliation-api?label=docker&logo=docker)]
   ```

4. **Trigger the pipeline**:
   ```bash
   # Commit your changes
   git add .
   git commit -m "feat: Add CI/CD pipeline and documentation"
   git push origin main
   
   # Create and push a version tag to trigger Docker build
   git tag v0.1.0
   git push origin v0.1.0
   ```

### Deployment

The Docker images are automatically built and pushed to Docker Hub on every tagged release:

```bash
# Pull the latest version
docker pull YOUR_DOCKER_USERNAME/contact-reconciliation-api:latest

# Or pull a specific version
docker pull YOUR_DOCKER_USERNAME/contact-reconciliation-api:v0.1.0

# Run the container
docker run -p 8000:8000 YOUR_DOCKER_USERNAME/contact-reconciliation-api:latest
```

## Troubleshooting

**Container won't start:**
```bash
# Check logs
docker-compose logs contact-api

# Check if port is in use
netstat -an | findstr :8000  # Windows
lsof -i :8000                # macOS/Linux
```

**Database issues:**
```bash
# Remove database and restart fresh
docker-compose down
rm -rf ./data
docker-compose up -d
```

**Docker Desktop issues:**
- Ensure Docker Desktop is running (whale icon in system tray)
- Try restarting Docker Desktop
- Check for Windows/macOS updates
```
