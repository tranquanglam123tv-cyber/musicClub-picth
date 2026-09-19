# Music Club Platform - Docker Configuration

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DOCKER ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │   Nginx     │──│  Backend    │──│   MySQL     │                │
│  │  (Reverse   │  │  (Spring   │  │  (Database) │                │
│  │   Proxy)    │  │   Boot)     │  │             │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
│        │                  │                                       │
│        │                  │                                        │
│        ▼                  ▼                                        │
│  ┌─────────────┐  ┌─────────────┐                                 │
│  │   Admin     │  │    DSP      │                                 │
│  │   (React)   │  │  (FastAPI)  │                                 │
│  └─────────────┘  └─────────────┘                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ============================================
  # NGINX - Reverse Proxy
  # ============================================
  nginx:
    image: nginx:alpine
    container_name: music_club_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - dsp-service
      - admin-web
    networks:
      - music_club_network
    restart: unless-stopped

  # ============================================
  # BACKEND - Spring Boot API
  # ============================================
  backend:
    build:
      context: ./docker/backend
      dockerfile: Dockerfile
    container_name: music_club_backend
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_NAME=music_club
      - DB_USER=musicclub
      - DB_PASSWORD=${DB_PASSWORD}
      - JWT_SECRET=${JWT_SECRET}
      - DSP_SERVICE_URL=http://dsp-service:8000
    ports:
      - "8080:8080"
    depends_on:
      mysql:
        condition: service_healthy
    networks:
      - music_club_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ============================================
  # DSP SERVICE - Python FastAPI
  # ============================================
  dsp-service:
    build:
      context: ./docker/dsp
      dockerfile: Dockerfile
    container_name: music_club_dsp
    environment:
      - PYTHONUNBUFFERED=1
    ports:
      - "8000:8000"
    networks:
      - music_club_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ============================================
  # ADMIN WEB - React
  # ============================================
  admin-web:
    build:
      context: ./docker/admin
      dockerfile: Dockerfile
    container_name: music_club_admin
    environment:
      - REACT_APP_API_URL=http://backend:8080/api
    networks:
      - music_club_network
    restart: unless-stopped

  # ============================================
  # MYSQL - Database
  # ============================================
  mysql:
    image: mysql:8.0
    container_name: music_club_mysql
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=music_club
      - MYSQL_USER=musicclub
      - MYSQL_PASSWORD=${DB_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
      - ./database/seed.sql:/docker-entrypoint-initdb.d/02-seed.sql:ro
    networks:
      - music_club_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  music_club_network:
    driver: bridge

volumes:
  mysql_data:
```

---

## Backend Dockerfile

```dockerfile
# docker/backend/Dockerfile

# Build stage
FROM maven:3.9-eclipse-temurin-17-alpine AS build
WORKDIR /app/backend

# Copy pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy source code and build
COPY src ./src
RUN mvn clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Copy jar file from build stage
COPY --from=build /app/backend/target/*.jar app.jar

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8080/api/health || exit 1

# Run
ENTRYPOINT ["java", "-jar", "-Xms256m", "-Xmx512m", "app.jar"]
```

---

## DSP Service Dockerfile

```dockerfile
# docker/dsp/Dockerfile

# Python runtime
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY dsp-service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY dsp-service/ ./app

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Admin Web Dockerfile

```dockerfile
# docker/admin/Dockerfile

# Build stage
FROM node:18-alpine AS build
WORKDIR /app

# Copy package files
COPY admin-web/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY admin-web/ ./

# Build
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY docker/nginx/admin.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
```

---

## Nginx Configuration

```nginx
# docker/nginx/nginx.conf

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript 
               application/xml application/xml+rss text/javascript application/x-javascript;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=1r/s;

    # Upstream servers
    upstream backend {
        server backend:8080;
        keepalive 32;
    }

    upstream dsp {
        server dsp-service:8000;
        keepalive 16;
    }

    server {
        listen 80;
        server_name localhost;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # API routes
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # DSP Service routes
        location /dsp/ {
            limit_req zone=upload_limit burst=5 nodelay;
            
            # Increase timeouts for file upload
            proxy_connect_timeout 120s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
            client_max_body_size 15M;

            rewrite ^/dsp/(.*) /$1 break;
            proxy_pass http://dsp;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Admin web (React SPA)
        location /admin/ {
            proxy_pass http://admin-web;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            return 200 'OK';
            add_header Content-Type text/plain;
        }

        # Root - Mobile app serves here
        location / {
            return 404 '{"error": "Not found"}';
            add_header Content-Type application/json;
        }
    }
}
```

---

## Environment Variables

```bash
# .env.example

# Database
MYSQL_ROOT_PASSWORD=YourStrongRootPassword123!
DB_PASSWORD=YourDatabasePassword123!

# JWT
JWT_SECRET=YourSuperSecretJWTTokenMustBeAtLeast256BitsLong!

# Application
SPRING_PROFILES_ACTIVE=prod
```

---

## Deployment Commands

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Restart specific service
docker-compose restart backend

# Scale DSP service
docker-compose up -d --scale dsp-service=3

# Execute command in container
docker-compose exec backend sh

# Database backup
docker-compose exec mysql mysqldump -u root -p music_club > backup.sql

# Database restore
docker-compose exec -T mysql mysql -u root -p music_club < backup.sql
```

---

## Health Checks

| Service | Endpoint | Expected |
|---------|----------|----------|
| Backend | GET /api/health | 200 OK |
| DSP Service | GET /api/v1/health | 200 OK |
| MySQL | ping | 0 |
| Nginx | GET /health | 200 OK |

---

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   docker-compose logs <service-name>
   ```

2. **Database connection failed**
   ```bash
   docker-compose exec mysql mysql -u musicclub -p
   ```

3. **Port already in use**
   ```bash
   lsof -i :80
   # or
   netstat -ano | findstr :80
   ```

4. **Out of memory**
   ```bash
   docker-compose down
   docker system prune -a
   docker-compose up -d
   ```

### Logs Location

| Service | Log Location |
|---------|-------------|
| Backend | docker-compose logs backend |
| DSP | docker-compose logs dsp-service |
| MySQL | docker-compose logs mysql |
| Nginx | docker-compose logs nginx |

---

**Document Version:** 1.0  
**Created:** September 19, 2026  
**Status:** Complete
