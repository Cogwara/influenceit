from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import CustomUser
from notifications.models import NotificationPreference
from django.shortcuts import render, redirect


@receiver(post_save, sender=CustomUser)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create default notification preferences for new users."""
    if created:
        # Create a single notification preference instance for the new user
        NotificationPreference.objects.create(
            user=instance,
            email_notifications=True,
            push_notifications=True,
            new_campaign_notifications=True,
            campaign_updates=True,
            campaign_deadlines=True,
            new_message_notifications=True,
            message_replies=True,
            new_follower_notifications=True,
            profile_mentions=True,
            platform_updates=True,
            newsletter=True
        )


def update_user_preferences(request, user_id):
    """Update user notification preferences"""
    user = CustomUser.objects.get(pk=user_id)
    if request.method == 'POST':
        prefs = NotificationPreference.objects.get(user=user)

        # Update each preference field
        prefs.email_notifications = request.POST.get(
            'email_notifications') == 'on'
        prefs.push_notifications = request.POST.get(
            'push_notifications') == 'on'
        prefs.new_campaign_notifications = request.POST.get(
            'new_campaign_notifications') == 'on'
        prefs.campaign_updates = request.POST.get('campaign_updates') == 'on'
        prefs.campaign_deadlines = request.POST.get(
            'campaign_deadlines') == 'on'
        prefs.new_message_notifications = request.POST.get(
            'new_message_notifications') == 'on'
        prefs.message_replies = request.POST.get('message_replies') == 'on'
        prefs.new_follower_notifications = request.POST.get(
            'new_follower_notifications') == 'on'
        prefs.profile_mentions = request.POST.get('profile_mentions') == 'on'
        prefs.platform_updates = request.POST.get('platform_updates') == 'on'
        prefs.newsletter = request.POST.get('newsletter') == 'on'

        prefs.save()
        return redirect('users:settings')

    return render(request, 'users/settings.html', {'user': user})
