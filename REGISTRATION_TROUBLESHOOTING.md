# Registration Troubleshooting Guide

If you're getting "Registration failed" error, follow these steps:

## 1. Check Browser Console
Open your browser's Developer Tools (F12) and check the Console tab. Look for:
- CORS errors (Cross-Origin Request Blocked)
- Network errors
- Any detailed error messages

## 2. Check Django Server Logs
Look at your Django server terminal. You should see the actual error there.

## 3. Common Issues & Fixes

### Issue: CORS Error
**Symptom:** Console shows "CORS policy" error or "Network Error"

**Fix:**
```bash
pip install django-cors-headers
```

Then update `agri_ai/settings.py`:
1. Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
    'rest_framework',
    'core.apps.CoreConfig',
]
```

2. Add to `MIDDLEWARE` (at the top, before other middleware):
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this first!
    'django.middleware.security.SecurityMiddleware',
    ...
]
```

3. Restart Django server

### Issue: Password Validation Failed
**Symptom:** Error mentions "password" or "too short"

**Fix:** Django requires passwords to be at least 8 characters. Make sure your password is 8+ characters and not too common.

### Issue: Backend Not Running
**Symptom:** "Cannot connect to server" error

**Fix:** Make sure Django is running:
```bash
python manage.py runserver
```

### Issue: Username Already Exists
**Symptom:** Error mentions username is taken

**Fix:** Choose a different username

## 4. Test Registration Manually

Test the API endpoint directly using curl or Postman:

```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "role": "farmer"
  }'
```

If this works, the issue is with the frontend. If it doesn't, check the Django server logs for the error.

## 5. Check Required Fields

Make sure you're filling in:
- Username (required)
- Password (required, min 8 chars)
- Confirm Password (must match)
- Role (farmer/agent/admin)

Email is optional.

