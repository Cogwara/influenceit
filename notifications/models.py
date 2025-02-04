from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('campaign', 'Campaign'),
        ('message', 'Message'),
        ('follower', 'New Follower'),
        ('mention', 'Mention'),
        ('update', 'Platform Update'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='system_notifications'
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} notification for {self.user.username}"


class NotificationPreference(models.Model):
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('both', 'Both'),
        ('none', 'None')
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES,
        default='email'
    )
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)

    # Campaign notifications
    new_campaign_notifications = models.BooleanField(default=True)
    campaign_updates = models.BooleanField(default=True)
    campaign_deadlines = models.BooleanField(default=True)

    # Message notifications
    new_message_notifications = models.BooleanField(default=True)
    message_replies = models.BooleanField(default=True)

    # Profile notifications
    new_follower_notifications = models.BooleanField(default=True)
    profile_mentions = models.BooleanField(default=True)

    # Platform notifications
    platform_updates = models.BooleanField(default=True)
    newsletter = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification preferences for {self.user.username}"

    def update_preferences(self, data):
        """Update notification preferences from form data"""
        for field in self._meta.fields:
            if field.name != 'id' and field.name != 'user':
                setattr(self, field.name, data.get(field.name) == 'on')
        self.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create default notification preferences for new users."""
    if created:
        preferences_to_create = []
        existing_types = set(NotificationPreference.objects.filter(
            user=instance
        ).values_list('notification_type', flat=True))

        for notification_type, _ in NotificationPreference.NOTIFICATION_TYPES:
            if notification_type not in existing_types:
                preferences_to_create.append(
                    NotificationPreference(
                        user=instance,
                        notification_type=notification_type,
                        email_notifications=True,
                        push_notifications=True
                    )
                )

        if preferences_to_create:
            NotificationPreference.objects.bulk_create(preferences_to_create)
