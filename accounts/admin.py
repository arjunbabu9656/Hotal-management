from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'room_number')
    list_filter = ('role',)
    search_fields = ('user__username', 'phone', 'room_number')
