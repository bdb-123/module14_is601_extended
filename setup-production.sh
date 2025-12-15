#!/bin/bash
# Complete CarCompare Setup Script for finalproject.bdb123.me

set -e  # Exit on error

echo "🚀 Setting up CarCompare at finalproject.bdb123.me..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as sudo for nginx setup
if [ "$EUID" -ne 0 ]; then 
   echo -e "${YELLOW}Note: You'll need sudo password for Nginx setup${NC}"
fi

# Navigate to project directory
cd ~/module14_is601_extended

echo -e "${GREEN}📦 Step 1: Pulling latest code from GitHub...${NC}"
git pull origin main || echo "Already up to date"

echo -e "${GREEN}🐳 Step 2: Deploying with Docker Compose...${NC}"
sudo docker compose -f docker-compose.prod.yml down || true
sudo docker compose -f docker-compose.prod.yml up -d --build

# Wait for containers to be ready
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 15

# Check if app is running
if sudo docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Docker containers are running${NC}"
else
    echo -e "${RED}❌ Docker containers failed to start${NC}"
    sudo docker compose -f docker-compose.prod.yml logs --tail=50
    exit 1
fi

echo -e "${GREEN}🔄 Step 3: Running database migrations...${NC}"
sudo docker compose -f docker-compose.prod.yml exec -T app alembic upgrade head || echo "Migrations completed or not needed"

echo -e "${GREEN}🌐 Step 4: Setting up Nginx...${NC}"

# Install Nginx if not already installed
if ! command -v nginx &> /dev/null; then
    echo "Installing Nginx..."
    sudo apt update
    sudo apt install -y nginx
fi

# Copy Nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/carcompare
sudo ln -sf /etc/nginx/sites-available/carcompare /etc/nginx/sites-enabled/carcompare

# Test Nginx configuration
if sudo nginx -t; then
    echo -e "${GREEN}✅ Nginx configuration is valid${NC}"
    sudo systemctl reload nginx
else
    echo -e "${RED}❌ Nginx configuration has errors${NC}"
    exit 1
fi

echo -e "${GREEN}🔒 Step 5: Setting up SSL with Let's Encrypt...${NC}"

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    sudo apt install -y certbot python3-certbot-nginx
fi

# Get SSL certificate
echo "Obtaining SSL certificate for finalproject.bdb123.me..."
sudo certbot --nginx -d finalproject.bdb123.me --non-interactive --agree-tos --email your-email@example.com || echo "SSL setup skipped or already configured"

echo ""
echo -e "${GREEN}✨ ========================================${NC}"
echo -e "${GREEN}   CarCompare Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}🌐 Your app is now live at:${NC}"
echo -e "   HTTP:  http://finalproject.bdb123.me"
echo -e "   HTTPS: https://finalproject.bdb123.me"
echo ""
echo -e "${YELLOW}📋 Useful commands:${NC}"
echo "   View logs:     cd ~/module14_is601_extended && sudo docker compose -f docker-compose.prod.yml logs -f"
echo "   Restart app:   cd ~/module14_is601_extended && sudo docker compose -f docker-compose.prod.yml restart"
echo "   Stop app:      cd ~/module14_is601_extended && sudo docker compose -f docker-compose.prod.yml down"
echo "   Update app:    cd ~/module14_is601_extended && git pull && sudo docker compose -f docker-compose.prod.yml up -d --build"
echo ""
echo -e "${GREEN}Container Status:${NC}"
sudo docker compose -f docker-compose.prod.yml ps
