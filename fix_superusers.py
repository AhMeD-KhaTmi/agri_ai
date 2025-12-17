#!/usr/bin/env python
"""Fix existing superusers to have admin role"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_ai.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import UserProfile

User = get_user_model()

# Fix all superusers
superusers = User.objects.filter(is_superuser=True)
fixed_count = 0

for user in superusers:
    profile, created = UserProfile.objects.get_or_create(user=user)
    if profile.role != 'admin':
        profile.role = 'admin'
        profile.save()
        fixed_count += 1
        print(f"✅ Updated {user.username} to admin role")
    else:
        print(f"✓ {user.username} already has admin role")

if fixed_count == 0 and superusers.count() == 0:
    print("No superusers found.")
elif fixed_count == 0:
    print(f"All {superusers.count()} superuser(s) already have admin role.")
else:
    print(f"\n✅ Fixed {fixed_count} superuser(s)!")

