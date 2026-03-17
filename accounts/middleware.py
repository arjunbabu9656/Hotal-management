from django.utils import timezone
from datetime import timedelta
from django.db import DatabaseError

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Lazy import to avoid circular dependencies
                from .models import UserProfile
                
                # Check for profile and update status if it exists
                # We catch DatabaseError too in case tables aren't migrated
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                
                now = timezone.now()
                last_seen = profile.last_seen
                
                if not last_seen or now > last_seen + timedelta(seconds=60):
                    profile.last_seen = now
                    profile.save(update_fields=['last_seen'])
            except (DatabaseError, Exception):
                # Never crash the entire site for status tracking
                pass
        
        response = self.get_response(request)
        return response
