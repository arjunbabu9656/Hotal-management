from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('staff', 'Staff'),
        ('manager', 'Manager'),
        ('owner', 'Owner'),
    )
    STAFF_ROLE_CHOICES = (
        ('none', 'None (Customer/Admin)'),
        ('computer', 'Computer/Front Desk'),
        ('kitchen', 'Kitchen Control'),
        ('cooker', 'Cooker'),
        ('cleaner', 'Cleaner'),
        ('delivery', 'Delivery Boy'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    staff_role = models.CharField(max_length=15, choices=STAFF_ROLE_CHOICES, default='none')
    phone = models.CharField(max_length=15, blank=True, null=True)
    room_number = models.CharField(max_length=10, blank=True, null=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    @property
    def is_online(self):
        if self.last_seen:
            from django.utils import timezone
            now = timezone.now()
            return now < self.last_seen + timezone.timedelta(minutes=5)
        return False

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
