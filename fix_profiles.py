import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_food.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def fix():
    users = User.objects.all()
    count = 0
    for user in users:
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user)
            print(f"Created profile for user: {user.username}")
            count += 1
    
    print(f"Finished fixing profiles. Created {count} missing profiles.")

if __name__ == "__main__":
    fix()
