import os
import django
from django.contrib.auth.hashers import make_password

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_food.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def seed_users():
    if not User.objects.filter(username='admin').exists():
        print("Creating admin user...")
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # Ensure the profile exists and set to owner
        profile, created = UserProfile.objects.get_or_create(user=admin_user)
        profile.role = 'owner'
        profile.save()
        print("Admin user created successfully (admin / admin123).")

if __name__ == '__main__':
    print("Running database seed...")
    try:
        seed_users()
        print("Database seed complete.")
    except Exception as e:
        print(f"Error seeding database: {e}")
