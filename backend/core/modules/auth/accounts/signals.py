from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=User)
def handle_user_status_change(sender, instance, **kwargs):
    """Handle user status changes (activation, deactivation)"""
    if instance.pk:  # Not a new user
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.is_active != instance.is_active:
                if not instance.is_active:
                    # User deactivated - revoke sessions
                    from .utils import revoke_user_sessions
                    revoke_user_sessions(instance)
        except User.DoesNotExist:
            pass  # New user
