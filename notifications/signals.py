from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_notification_preferences(sender, instance, created, **kwargs):
    """Create notification preferences when a new user is created"""
    if created:
        from notifications.models import NotificationPreference
        NotificationPreference.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_notification_preferences(sender, instance, **kwargs):
    """Save notification preferences when user is saved"""
    try:
        if hasattr(instance, 'notification_preferences'):
            instance.notification_preferences.save()
    except Exception:
        from notifications.models import NotificationPreference
        NotificationPreference.objects.create(user=instance)
