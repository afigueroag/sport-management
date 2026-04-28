# SportAcademia Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development with Docker](#local-development-with-docker)
3. [Production Deployment](#production-deployment)
4. [Security Best Practices](#security-best-practices)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Docker**: 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: 1.29+ ([Install Docker Compose](https://docs.docker.com/compose/install/))
- **Git**: For cloning the repository

### Stripe Account
- Create a Stripe account at https://stripe.com
- Get API keys from https://dashboard.stripe.com/apikeys
- Create webhook endpoint for your deployment URL

---

## Local Development with Docker

### 1. Clone Repository
```bash
git clone <repository-url>
cd sport-management
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your local settings:
```env
DEBUG=True
DB_PASSWORD=your-local-password
SECRET_KEY=your-local-secret-key
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### 3. Start Services
```bash
docker-compose up -d
```

This will:
- ✓ Build the FastAPI app image
- ✓ Start PostgreSQL database
- ✓ Create network bridge between services
- ✓ Run health checks

### 4. Verify Services
```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs -f app

# Test API
curl http://localhost:8000/health
```

### 5. Access Application
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Database**: `postgresql://postgres:password@localhost:5432/sport_academy`

### 6. Stop Services
```bash
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v
```

---

## Production Deployment

### Recommended: Using a VPS with Docker

#### 1. Prepare Server (Ubuntu 22.04 LTS)
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
mkdir -p /app/sport-academy
cd /app/sport-academy
```

#### 2. Deploy Application
```bash
# Clone repository
git clone <repository-url> .

# Create production .env
nano .env
```

**Production .env template:**
```env
# Application
DEBUG=False
APP_NAME=SportAcademia
APP_VERSION=0.1.0

# Database
DB_USER=sport_academy_user
DB_PASSWORD=generate-strong-password-here
DB_NAME=sport_academy
DATABASE_URL=postgresql+asyncpg://sport_academy_user:generate-strong-password-here@db:5432/sport_academy

# Security (Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=generate-random-string-here

# CORS
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# Stripe
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

#### 3. Start Production Services
```bash
# Start in detached mode
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app

# Verify health
curl http://localhost:8000/health
```

#### 4. Setup Nginx Reverse Proxy (Optional)
```bash
sudo apt-get install -y nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/sport-academy
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/sport-academy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Setup SSL (Let's Encrypt)
```bash
sudo apt-get install -y certbot python3-certbot-nginx

sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### 6. Setup Auto-Updates
```bash
# Create update script
cat > /app/sport-academy/update.sh << 'EOF'
#!/bin/bash
cd /app/sport-academy
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
docker-compose logs -f app
EOF

chmod +x /app/sport-academy/update.sh

# Add to crontab for daily updates at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /app/sport-academy/update.sh") | crontab -
```

---

## Security Best Practices

### 1. Environment Variables
- ✓ Never commit `.env` to git
- ✓ Use `.env.example` as template
- ✓ Generate strong SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- ✓ Use 20+ character database password

### 2. Database
- ✓ Change default PostgreSQL password
- ✓ Use non-root user for connections
- ✓ Enable SSL for remote connections
- ✓ Regular backups: `docker-compose exec db pg_dump -U postgres sport_academy > backup.sql`

### 3. API Security
- ✓ Set `DEBUG=False` in production
- ✓ Restrict CORS_ORIGINS to your domain
- ✓ Keep SECRET_KEY secret (rotate if compromised)
- ✓ Monitor API logs for suspicious activity

### 4. Docker Security
- ✓ Use non-root user (already configured in Dockerfile)
- ✓ Keep base images updated: `docker-compose build --no-cache`
- ✓ Don't expose unnecessary ports
- ✓ Use health checks (already configured)

### 5. Stripe Integration
- ✓ Use `sk_live_` keys in production (not `sk_test_`)
- ✓ Validate webhook signatures (code does this automatically)
- ✓ Rotate webhook secrets regularly
- ✓ Monitor failed payments in Stripe dashboard

### 6. Monitoring & Logging
- ✓ Configure log aggregation (ELK, Datadog, etc.)
- ✓ Monitor application errors
- ✓ Track database performance
- ✓ Setup alerts for high error rates

---

## Troubleshooting

### Issue: Container won't start
```bash
# Check logs
docker-compose logs app

# Common causes:
# - Database connection failed: Wait for DB to be ready
# - Port 8000 already in use: Change port in docker-compose.yml
# - Environment variable missing: Check .env file
```

### Issue: Database connection error
```bash
# Check if database is running
docker-compose ps db

# Verify database is healthy
docker-compose exec db pg_isready -U postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

### Issue: Stripe webhook not working
```bash
# Check webhook logs
docker-compose logs app | grep webhook

# Verify Stripe webhook secret in .env
# Webhook must be accessible from internet (not localhost)
# Use ngrok for local testing: ngrok http 8000
```

### Issue: Out of disk space
```bash
# Clean up Docker
docker system prune -a

# Remove old logs
docker-compose exec app sh -c 'find /app -name "*.log" -delete'
```

### Reset Everything
```bash
# Stop and remove everything
docker-compose down -v

# Remove unused images
docker image prune -a

# Start fresh
docker-compose up -d
```

---

## Backup & Recovery

### Automated Database Backups
```bash
# Create backup directory
mkdir -p /backups

# Backup database
docker-compose exec db pg_dump -U postgres sport_academy > /backups/sport_academy_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker-compose exec -T db psql -U postgres sport_academy < /backups/sport_academy_TIMESTAMP.sql
```

### Backup Script (Daily at 3 AM)
```bash
cat > /app/sport-academy/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
cd /app/sport-academy
docker-compose exec -T db pg_dump -U postgres sport_academy > $BACKUP_DIR/backup_$DATE.sql
# Keep last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /app/sport-academy/backup.sh
(crontab -l 2>/dev/null; echo "0 3 * * * /app/sport-academy/backup.sh") | crontab -
```

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f app`
2. Review error messages in Stripe dashboard
3. Check database connection in PostgreSQL
4. Verify environment variables in `.env`

