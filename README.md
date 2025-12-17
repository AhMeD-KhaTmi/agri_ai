# Agri AI – Project Overview

This single document summarizes the **essential information** from:
`FINAL_SPECIFICATION_REVIEW.md`, `SPECIFICATION_CHECKLIST.md`, `TESTING_GUIDE.md`,
`HOW_TO_GENERATE_ANOMALIES.md`, `WEEK3_COMPLETE.md`, and `REGISTRATION_TROUBLESHOOTING.md`.

## 1. Stack & Architecture
- **Backend**: Django 6, Django REST Framework, PostgreSQL
- **Auth**: JWT (SimpleJWT), roles: `farmer`, `admin`
- **Core models**: `FarmProfile`, `FieldPlot`, `SensorReading`, `AnomalyEvent`, `AgentRecommendation`, `UserProfile`
- **ML Module**: threshold + rolling statistics + time‑aware anomalies (sudden drop, drift)
- **AI Agent**: rule‑based recommendations + human‑readable explanations
- **Frontend**: React (Create React App), Chart.js for time‑series plots
- **Simulation**: Python script `simulator/simulator.py` sends sensor data to the API

## 2. Backend Setup (PostgreSQL)
1. Create database and user in PostgreSQL:
   ```sql
   CREATE DATABASE agri_db;
   CREATE USER agri_user WITH PASSWORD 'agri_pass';
   ALTER ROLE agri_user CREATEDB;
   GRANT ALL PRIVILEGES ON DATABASE agri_db TO agri_user;
   GRANT ALL ON SCHEMA public TO agri_user;
   ```
2. Install deps & run migrations:
   ```bash
   pipenv install
   pipenv run python manage.py migrate
   pipenv run python manage.py createsuperuser  # optional
   ```
3. Run backend:
   ```bash
   pipenv run python manage.py runserver
   ```

## 3. Frontend Setup
From `frontend/`:
```bash
npm install
npm start
```
Frontend runs at `http://localhost:3000` and talks to `http://127.0.0.1:8000/api`.

### Main Pages
- `/login` – JWT login
- `/dashboard` – list of plots + status indicators
- `/plot/:plotId` – time‑series charts
- `/alerts` – anomalies + AI recommendations

## 4. Roles & Permissions
- **farmer**:
  - Sees only their own `FarmProfile`/`FieldPlot`
  - Only their plots' `SensorReading`, `AnomalyEvent`, `AgentRecommendation`
- **admin**:
  - Sees **all** farms, plots, anomalies, recommendations
  - Can use Django admin to manage users and assign roles
- **superuser** (Django superuser):
  - Automatically gets `admin` role in `UserProfile` when created
  - Has full admin access to all data (same as admin role)
  - Can access Django admin interface at `/admin/`
  - If you have existing superusers, run `python fix_superusers.py` to update their roles

## 5. Simulator & Anomaly Generation
Script: `simulator/simulator.py`

Example usage (with anomalies across multiple plots):
```bash
pipenv run python simulator/simulator.py \
  --plots 1 2 3 4 \
  --freq 5 \
  --inject_anomaly \
  --anomaly_every 5 \
  --username farmer1 \
  --password testpw123
```
- Generates realistic diurnal patterns for **moisture**, **temperature**, **humidity**.
- Each (plot, sensor) reading has a random chance of being anomalous.
- Backend ML module detects anomalies and `signals.py` creates `AnomalyEvent` + `AgentRecommendation`.

## 6. Testing & Evaluation
Run tests:
```bash
pipenv run python manage.py test
```
- `test_anomalies.py` – validates anomaly creation logic
- `test_evaluation.py` – evaluates ML metrics and system behavior
- `core/tests2.py` – end‑to‑end tests for sensor → anomaly → recommendation

## 7. Security Checklist
- JWT authentication for all protected APIs
- Role‑based authorization (`farmer`, `admin`)
- Validation via DRF serializers (no raw SQL)
- Proper HTTP codes on errors (400, 401, 403, 500)
- Secrets (DB creds, JWT secret) should be stored in `.env` and not committed

## 8. Docker Deployment

**🚀 One-Command Setup**: After cloning, just copy `.env.example` to `.env` and run `docker-compose up`!

### Prerequisites
- Docker Desktop installed and running

### Quick Start with Docker Compose

1. **Copy `.env.example` to `.env`**:
   ```bash
   # On Windows (PowerShell)
   Copy-Item .env.example .env
   
   # On Linux/Mac
   cp .env.example .env
   ```
   
   This creates the `.env` file with default configuration. You can edit `.env` to customize settings if needed.

2. **Build and start all services**:
   ```bash
   docker-compose build
   docker-compose up
   ```
   
   **Note**: If you get an error about `.env` file not found, make sure you completed step 1 above.

3. **Access the application**:
   - Frontend: http://localhost:3000 (served by nginx, proxies API calls to backend)
   - Backend API: http://localhost:8000 (direct access)
   - Django Admin: http://localhost:8000/admin/

### Docker Services
- **`db`**: PostgreSQL 15 database (port 5432 exposed)
- **`backend`**: Django application (port 8000 exposed, auto-runs migrations + creates default user)
- **`frontend`**: React app built and served via nginx (port 3000)
- **`simulator`**: Python simulator running automatically (sends data to backend via Docker network)

**Everything runs automatically!** Just `docker-compose up` and all services start together.

**Note**: The backend port (8000) is exposed to the host, allowing direct access to:
- Django admin: http://localhost:8000/admin/
- API endpoints: http://localhost:8000/api/
- The simulator connects internally using the service name `backend:8000`

### Useful Docker Commands
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# View logs
docker-compose logs -f backend

# View simulator logs
docker-compose logs -f simulator

# Create superuser
docker-compose run --rm backend python manage.py createsuperuser

# Fix existing superusers to have admin role
docker-compose exec backend python fix_superusers.py
```

## 9. Recent Fixes & Improvements

### Simulator Connection Issue (Fixed)
**Problem**: The simulator container couldn't connect to the backend, showing `ERR_CONNECTION_REFUSED` errors.

**Root Cause**: Django's `ALLOWED_HOSTS` setting only included `'localhost'` and `'127.0.0.1'`, but the simulator connects using the Docker service name `'backend'`, which Django rejected.

**Solution**: Added `'backend'` to `ALLOWED_HOSTS` in `agri_ai/settings.py`:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'backend']
```

**Result**: Simulator now successfully connects and sends sensor data to the backend. Backend logs show successful POST requests (201 status codes) to `/api/sensor-readings/`.

### Admin Role & Permissions Issue (Fixed)
**Problem**: Django superusers couldn't see all plots in the Django admin interface or via API endpoints, even though they should have admin privileges.

**Root Causes**:
1. Django superusers didn't automatically get `role='admin'` in their `UserProfile` - they defaulted to `'farmer'`
2. API views only checked `UserProfile.role`, not `user.is_superuser` status
3. Django admin interface didn't have custom filtering to show all data for admins

**Solutions Implemented**:

1. **Updated `core/models.py`**: Modified the `create_user_profile` signal to automatically set `role='admin'` when a superuser is created:
   ```python
   @receiver(post_save, sender=settings.AUTH_USER_MODEL)
   def create_user_profile(sender, instance, created, **kwargs):
       if created:
           profile = UserProfile.objects.create(user=instance)
           if instance.is_superuser:
               profile.role = 'admin'
               profile.save()
   ```

2. **Updated `core/views.py`**: Modified all view querysets to check both `is_superuser` and `role`:
   - `FieldPlotListView`: Superusers and admins see all plots
   - `AnomalyListView`: Superusers and admins see all anomalies
   - `RecommendationListView`: Superusers and admins see all recommendations
   - `RolePermission`: Updated to grant admin permissions to superusers

3. **Enhanced `core/admin.py`**: Added custom admin classes with:
   - Better list displays and filtering
   - Automatic admin role assignment when saving superusers
   - Improved search and filtering capabilities

4. **Created `fix_superusers.py`**: Utility script to fix existing superusers:
   ```bash
   docker-compose exec backend python fix_superusers.py
   ```

**Result**: 
- Django superusers now automatically get admin role
- Superusers can see all plots, farms, anomalies, and recommendations
- Both Django admin interface and API endpoints respect admin permissions
- Existing superusers can be fixed using the provided script

### Docker Port Configuration (Fixed)
**Problem**: Backend port wasn't exposed in Docker, preventing access to Django admin.

**Solution**: Changed `expose` to `ports` in `docker-compose.yml`:
```yaml
backend:
  ports:
    - "8000:8000"  # Changed from expose: - "8000"
```

**Result**: Django admin is now accessible at `http://localhost:8000/admin/` and shows up in Docker Desktop port mappings.

### Summary of Files Modified
- `agri_ai/settings.py`: Added `'backend'` to `ALLOWED_HOSTS`
- `core/admin.py`: Added custom admin classes with proper filtering
- `core/views.py`: Updated to check `is_superuser` in addition to role checks
- `core/models.py`: Updated signal to set admin role for superusers
- `docker-compose.yml`: Changed `expose` to `ports` for backend service
- `fix_superusers.py`: New utility script to fix existing superusers

All fixes are backward compatible and don't break existing functionality.

This README is the **single entry point**; use the other `.md` files only for detailed grading/spec references if needed.
