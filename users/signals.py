from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.conf import settings  # To get AUTH_USER_MODEL
from .models import CustomUser, InfluencerProfile, BrandProfile
from notifications.models import NotificationPreference
from django.shortcuts import render, redirect
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import NotificationPreference
from .models import CustomUser

# Set up logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_preferences_and_profiles(sender, instance, created, **kwargs):
    """
    Create NotificationPreferences and relevant profiles when a new user is created.
    """
    if created:
        logger.info(f"Creating NotificationPreferences and profiles for user: {
                    instance.email}")
        with transaction.atomic():
            # Use lazy imports to prevent circular dependencies
            from notifications.models import NotificationPreference
            NotificationPreference.objects.get_or_create(user=instance)

            if instance.user_type == 'influencer':
                from users.models import InfluencerProfile
                InfluencerProfile.objects.get_or_create(user=instance)
            elif instance.user_type in ['brand', 'seeker']:
                from users.models import BrandProfile
                BrandProfile.objects.get_or_create(user=instance)


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
