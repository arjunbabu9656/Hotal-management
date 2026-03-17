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
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            print(f"Created profile for user: {user.username}")
            count += 1
        
        # Ensure superusers always have the 'owner' role for full portal access
        if user.is_superuser and profile.role != 'owner':
            profile.role = 'owner'
            profile.save()
            print(f"Updated {user.username} to 'owner' role.")
    
    # Phase 2: Cleanup orphaned profiles
    orphans = UserProfile.objects.filter(user__isnull=True)
    orphan_count = orphans.count()
    if orphan_count > 0:
        orphans.delete()
        print(f"Deleted {orphan_count} orphaned profiles.")
    
    print(f"Finished fixing profiles. Created {count} missing, cleaned {orphan_count} orphans.")

if __name__ == "__main__":
    fix()
