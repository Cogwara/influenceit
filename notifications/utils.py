from .models import NotificationPreference

def create_default_preferences(user):
    """Create default notification preferences for a user."""
    default_preferences = []
    for notification_type, _ in NotificationPreference.NOTIFICATION_TYPES:
        default_preferences.append(
            NotificationPreference(
                user=user,
                notification_type=notification_type,
                email_enabled=True,
                push_enabled=True
            )
        )
    NotificationPreference.objects.bulk_create(default_preferences) 