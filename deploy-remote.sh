#!/bin/bash
# PXMX Remote Deployment Script
# Deploy to: manage.koetsier.it
# Location: /opt/pxmx

set -e

SERVER="manage.koetsier.it"
DEPLOY_DIR="/opt/pxmx"
REPO_URL="https://github.com/jskoetsier/pxpx.git"

echo "🚀 PXMX Remote Deployment Script"
echo "================================="
echo "Server: $SERVER"
echo "Directory: $DEPLOY_DIR"
echo ""

# Check if we can connect to the server
echo "📡 Testing connection to $SERVER..."
if ! ssh root@$SERVER "echo 'Connection successful'"; then
    echo "❌ Cannot connect to $SERVER"
    echo "Please ensure:"
    echo "  1. You have SSH access configured"
    echo "  2. Your SSH key is added to the server"
    exit 1
fi

echo "✅ Connection successful!"
echo ""

# Deploy to remote server
echo "📦 Deploying to $SERVER:$DEPLOY_DIR..."

ssh root@$SERVER << 'ENDSSH'
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting deployment...${NC}"

# Create directory
echo -e "${YELLOW}📁 Creating deployment directory...${NC}"
mkdir -p /opt/pxmx
cd /opt/pxmx

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Installing git...${NC}"
    dnf install -y git || yum install -y git || apt-get install -y git
fi

# Clone or update repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}📥 Updating existing repository...${NC}"
    git pull origin main
else
    echo -e "${YELLOW}📥 Cloning repository...${NC}"
    git clone https://github.com/jskoetsier/pxpx.git .
fi

# Create production environment file
echo -e "${YELLOW}⚙️  Creating production environment file...${NC}"
cat > .env << 'EOF'
# Production Configuration
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=manage.koetsier.it,localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://pxmx_user:$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)@db:5432/pxmx_db

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Security
PROXMOX_VERIFY_SSL=False
EOF

# Generate a proper secret key
SECRET_KEY=$(openssl rand -base64 48 | tr -d "=+/" | cut -c1-50)
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

cat > .env << EOF
# Production Configuration
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=manage.koetsier.it,localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://pxmx_user:$DB_PASSWORD@db:5432/pxmx_db

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Security
PROXMOX_VERIFY_SSL=False
EOF

echo -e "${GREEN}✅ Environment file created${NC}"

# Update docker-compose for production
echo -e "${YELLOW}⚙️  Updating docker-compose for production...${NC}"
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: pxmx_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=pxmx_db
      - POSTGRES_USER=pxmx_user
      - POSTGRES_PASSWORD=${DATABASE_URL##*:}
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pxmx_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: pxmx_redis
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  web:
    build: .
    container_name: pxmx_web
    command: gunicorn --workers 3 --bind 0.0.0.0:8000 pxmx.wsgi:application
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  celery:
    build: .
    container_name: pxmx_celery
    command: celery -A pxmx worker --loglevel=info
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
EOF

echo -e "${GREEN}✅ docker-compose.yml updated for production${NC}"

# Check if podman-compose is installed
echo -e "${YELLOW}🔍 Checking for podman-compose...${NC}"
if ! command -v podman-compose &> /dev/null; then
    echo -e "${YELLOW}Installing podman-compose...${NC}"
    pip3 install podman-compose || python3 -m pip install podman-compose
fi

echo -e "${GREEN}✅ podman-compose is available${NC}"

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
podman-compose down 2>/dev/null || true

# Build and start services
echo -e "${YELLOW}🏗️  Building containers...${NC}"
podman-compose build

echo -e "${YELLOW}🚀 Starting services...${NC}"
podman-compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Show status
echo -e "${YELLOW}📊 Container status:${NC}"
podman-compose ps

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "🌐 Access your dashboard at: http://manage.koetsier.it:8000"
echo "👤 Default login: admin / admin"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Change the default admin password immediately!${NC}"
echo ""
echo "📝 Useful commands:"
echo "  podman-compose logs -f          # View logs"
echo "  podman-compose restart          # Restart services"
echo "  podman-compose down             # Stop services"
echo "  podman-compose exec web bash    # Access web container"
echo ""

ENDSSH

echo ""
echo "✅ Deployment script completed!"
echo ""
echo "🌐 Your PXMX dashboard should now be accessible at:"
echo "   http://manage.koetsier.it:8000"
echo ""
echo "👤 Login with: admin / admin"
echo "   (Change this password immediately!)"
echo ""
