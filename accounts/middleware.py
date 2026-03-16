from django.utils import timezone
from datetime import timedelta

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = timezone.now()
            # Only update if last_seen is older than 60 seconds to avoid constant DB writes
            last_seen = request.user.profile.last_seen
            
            if not last_seen or now > last_seen + timedelta(seconds=60):
                request.user.profile.last_seen = now
                request.user.profile.save(update_fields=['last_seen'])
        
        response = self.get_response(request)
        return response
