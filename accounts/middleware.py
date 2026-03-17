from django.utils import timezone
from datetime import timedelta

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                now = timezone.now()
                last_seen = profile.last_seen
                
                if not last_seen or now > last_seen + timedelta(seconds=60):
                    profile.last_seen = now
                    profile.save(update_fields=['last_seen'])
            except:
                # Fallback if profile doesn't exist yet
                pass
        
        response = self.get_response(request)
        return response
