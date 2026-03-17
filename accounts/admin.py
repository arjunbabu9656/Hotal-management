from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# 1. Define the Profile Inline
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Details'
    fk_name = 'user'

# 2. Rebuild the main UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_select_related = ('profile', )

    def get_role(self, instance):
        try:
            if hasattr(instance, 'profile') and instance.profile:
                return instance.profile.get_role_display()
            return "No Profile"
        except Exception:
            return "Error Loading Role"
    get_role.short_description = 'User Role'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

# 3. Safe Re-registration
from django.contrib.admin.sites import NotRegistered
try:
    admin.site.unregister(User)
except NotRegistered:
    pass
admin.site.register(User, UserAdmin)

# 4. Optional: Register UserProfile separately for direct access
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('safe_user', 'role', 'phone', 'room_number')
    list_filter = ('role', 'staff_role')
    search_fields = ('user__username', 'phone')

    def safe_user(self, obj):
        try:
            if obj.user:
                return obj.user.username
        except Exception:
            pass
        return "N/A (No User)"
    safe_user.short_description = 'User'
