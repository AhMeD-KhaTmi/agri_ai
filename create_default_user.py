#!/usr/bin/env python
"""Create default user, farm, and plot for simulator if they don't exist"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_ai.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import UserProfile, FarmProfile, FieldPlot

User = get_user_model()

username = 'farmer1'
password = 'testpw123'

# Create user if doesn't exist
if not User.objects.filter(username=username).exists():
    print(f"Creating default user: {username}")
    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password=password
    )
    # UserProfile is created automatically by signal, but ensure role is set
    if hasattr(user, 'userprofile'):
        user.userprofile.role = 'farmer'
        user.userprofile.save()
    print(f"✅ User '{username}' created successfully!")
else:
    user = User.objects.get(username=username)
    print(f"User '{username}' already exists.")

# Create farm if doesn't exist
farm, created = FarmProfile.objects.get_or_create(
    owner=user,
    defaults={
        'location': 'Test Farm',
        'crop_type': 'Wheat'
    }
)
if created:
    print(f"✅ Farm 'Test Farm' created for {username}!")
else:
    print(f"Farm already exists for {username}.")

# Create plot with ID 1 if doesn't exist
plot, created = FieldPlot.objects.get_or_create(
    id=1,
    defaults={
        'farm': farm,
        'name': 'Plot 1',
        'crop_variety': 'Winter Wheat'
    }
)
if created:
    print(f"✅ Plot 1 created for simulator!")
else:
    print(f"Plot 1 already exists.")
