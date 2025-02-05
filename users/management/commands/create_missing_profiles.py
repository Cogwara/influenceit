from django.core.management.base import BaseCommand
from users.models import CustomUser, InfluencerProfile, BrandProfile
from notifications.models import NotificationPreference
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create missing profiles and NotificationPreferences for existing users.'

    def handle(self, *args, **options):
        users = CustomUser.objects.all()
        for user in users:
            with transaction.atomic():
                # Create NotificationPreference if missing
                NotificationPreference.objects.get_or_create(user=user)

                # Create InfluencerProfile or BrandProfile based on user_type
                if user.user_type == 'influencer' and not hasattr(user, 'influencerprofile'):
                    InfluencerProfile.objects.create(user=user)
                    self.stdout.write(self.style.SUCCESS(
                        f"Created InfluencerProfile for {user.email}"))

                elif user.user_type in ['brand', 'seeker'] and not hasattr(user, 'brandprofile'):
                    BrandProfile.objects.create(user=user)
                    self.stdout.write(self.style.SUCCESS(
                        f"Created BrandProfile for {user.email}"))
        self.stdout.write(self.style.SUCCESS(
            'Missing profiles and NotificationPreferences have been created successfully.'))

        users_without_pref = User.objects.filter(
            notificationpreference__isnull=True)
        total = users_without_pref.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS(
                'All users have NotificationPreferences.'))
            return

        self.stdout.write(
            f'Creating NotificationPreferences for {total} users...')

        with transaction.atomic():
            NotificationPreference.objects.bulk_create([
                NotificationPreference(user=user)
                for user in users_without_pref
            ], ignore_conflicts=True)  # ignore_conflicts=True skips duplicates

        self.stdout.write(self.style.SUCCESS(
            'Successfully created missing NotificationPreferences.'))
