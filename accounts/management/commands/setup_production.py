from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
import os

class Command(BaseCommand):
    help = 'Ensures superuser and user profiles are correctly configured for production'

    def handle(self, *args, **options):
        # 1. Handle Superuser
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')

        if username and password:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, password=password, email=email)
                self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
            else:
                self.stdout.write(f"Superuser '{username}' already exists.")

        # 2. Fix/Sync Profiles
        users = User.objects.all()
        created_count = 0
        updated_count = 0
        for user in users:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                created_count += 1
            
            # Absolute control: Superusers MUST be owners
            if user.is_superuser and profile.role != 'owner':
                profile.role = 'owner'
                profile.save()
                updated_count += 1
        
        # 3. Cleanup Orphans
        orphans = UserProfile.objects.filter(user__isnull=True)
        orphan_count = orphans.count()
        orphans.delete()

        self.stdout.write(self.style.SUCCESS(
            f"Sync complete: Created {created_count}, Updated {updated_count}, Cleaned {orphan_count} orphans."
        ))
