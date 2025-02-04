from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, NotificationPreference
from django.shortcuts import render, redirect
from .models import NotificationPreference


@receiver(post_save, sender=CustomUser)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create default notification preferences for new users."""
    if created:
        preferences = [
            NotificationPreference(
                user=instance, notification_type=nt[0], email_enabled=True, push_enabled=True)
            for nt in NotificationPreference.NOTIFICATION_TYPES
        ]
        NotificationPreference.objects.bulk_create(preferences)
    else:
        # Assuming you have a list of preference instances to be associated
        existing_preferences = NotificationPreference.objects.filter(
            user=instance)
        instance.notification_preferences.set(existing_preferences)


def update_user_preferences(request, user_id):
    user = CustomUser.objects.get(pk=user_id)
    if request.method == 'POST':
        for pref in user.notification_preferences.all():
            email_enabled = request.POST.get(
                f'email_{pref.notification_type}', False)
            push_enabled = request.POST.get(
                f'push_{pref.notification_type}', False)
            pref.email_enabled = email_enabled == 'on'
            pref.push_enabled = push_enabled == 'on'
            pref.save()
        return redirect('some_view_name')
    return render(request, 'some_template.html', {'user': user})
