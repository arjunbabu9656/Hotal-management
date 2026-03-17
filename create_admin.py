import os
import django

# Set settings BEFORE importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_food.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')

    if username and password:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, password=password, email=email)
            print(f"Superuser '{username}' created successfully.")
        else:
            print(f"Superuser '{username}' already exists. Skipping creation.")

if __name__ == "__main__":
    create_admin()
