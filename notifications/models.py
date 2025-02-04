from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

# Notifications App - Handle system notifications
class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications_received'
    )
    type = models.CharField(max_length=50)
    content = models.JSONField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class NotificationPreference(models.Model):
    NOTIFICATION_TYPES = [
        ('campaign_update', 'Campaign Updates'),
        ('contract_update', 'Contract Updates'),
        ('payment_update', 'Payment Updates'),
        ('message_received', 'Messages'),
        ('review_received', 'Reviews'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'notification_type']

    def __str__(self):
        return f"{self.user.email} - {self.get_notification_type_display()}"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create default notification preferences for new users."""
    if created:
        default_preferences = []
        for notification_type, _ in NotificationPreference.NOTIFICATION_TYPES:
            default_preferences.append(
                NotificationPreference(
                    user=instance,
                    notification_type=notification_type,
                    email_enabled=True,
                    push_enabled=True
                )
            )
        NotificationPreference.objects.bulk_create(default_preferences)
