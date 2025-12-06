# Quick Setup Guide

## 🚀 Steps to Run Frontend

1. **Navigate to frontend folder:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install --legacy-peer-deps
   ```
   This installs:
   - react-router-dom (routing)
   - axios (API calls)
   - chart.js & react-chartjs-2 (charts)
   - All other React dependencies

3. **Make sure Django backend is running:**
   ```bash
   # In another terminal, in project root:
   python manage.py runserver
   ```

4. **Start React frontend:**
   ```bash
   npm start
   ```
   Opens at http://localhost:3000

## 🔑 Login Credentials

Use any user you created in Django admin. Make sure the user has a UserProfile with role set to 'farmer', 'agent', or 'admin'.

## 📋 Features Implemented

✅ **Login Page** - JWT authentication
✅ **Dashboard** - List plots with status indicators (healthy/warning/critical)
✅ **Plot Detail** - Interactive time-series charts for moisture/temperature/humidity
✅ **Alerts Page** - Shows all anomalies with AI agent recommendations
✅ **Navigation** - Protected routes, logout functionality
✅ **API Integration** - All endpoints connected to Django backend

## 🐛 Troubleshooting

**CORS errors?** Make sure Django has CORS headers enabled. Add to `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

**401 Unauthorized?** Make sure you're logged in and the token is valid.

**No data showing?** Ensure you have:
- Created plots in Django admin
- Sent sensor readings (via simulator or API)
- Anomalies detected (triggers recommendations automatically)

