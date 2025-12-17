# Agri AI – Quick Command Reference

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Copy environment file
Copy-Item .env.example .env    # Windows PowerShell
# OR
cp .env.example .env           # Linux/Mac

# 2. Build and start all services
docker-compose build
docker-compose up
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/

---

## 📋 Essential Commands

### Start/Stop Services
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove all data (fresh start)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f simulator
docker-compose logs -f db
```

### Rebuild Services
```bash
# Rebuild all
docker-compose build

# Rebuild specific service
docker-compose build frontend
docker-compose build backend

# Rebuild with no cache (clean build)
docker-compose build --no-cache frontend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

---

## 👤 User Management

### Create Django Superuser
```bash
docker-compose run --rm backend python manage.py createsuperuser
```

### Fix Existing Superusers (give them admin role)
```bash
docker-compose exec backend python fix_superusers.py
```

---

## 🔧 Troubleshooting Commands

### PostgreSQL Version Mismatch
```bash
# Remove old volumes and start fresh
docker-compose down -v
docker-compose up

# Or remove specific volume
docker volume rm agri_ai-main_postgres_data
docker-compose up
```

### Frontend Not Loading (ERR_EMPTY_RESPONSE)
```bash
# Check frontend status
docker-compose ps frontend

# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up frontend

# Check if files exist in container
docker-compose exec frontend ls -la /usr/share/nginx/html

# Test nginx inside container
docker-compose exec frontend curl http://localhost
```

### Port Already in Use
```bash
# Check what's using port (Windows)
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Check what's using port (Linux/Mac)
lsof -i :3000
lsof -i :8000
```

### Missing .env File
```bash
# Create .env file
Copy-Item .env.example .env    # Windows PowerShell
cp .env.example .env           # Linux/Mac
```

### Complete Fresh Start
```bash
# Stop everything, remove volumes, rebuild, and start
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

---

## 🧪 Testing & Development

### Run Tests
```bash
docker-compose exec backend python manage.py test
```

### Run Migrations
```bash
docker-compose exec backend python manage.py migrate
```

### Access Django Shell
```bash
docker-compose exec backend python manage.py shell
```

### Check Container Status
```bash
docker-compose ps
```

---

## 📦 Project Structure

- **Backend**: Django 6 + DRF + PostgreSQL
- **Frontend**: React + Chart.js (served via nginx)
- **Simulator**: Python script (auto-runs in Docker)
- **Database**: PostgreSQL 15

### Default Test User
- **Username**: `farmer1`
- **Password**: `testpw123`
- Created automatically on first run

---

## 🔐 Roles

- **farmer**: Sees only their own farms/plots
- **admin**: Sees all farms/plots (can be assigned in Django admin)

---

## 📝 Notes

- All services start automatically with `docker-compose up`
- Simulator sends data automatically to plot ID 1
- Default user (`farmer1`) and test farm are created automatically
- Superusers automatically get `admin` role