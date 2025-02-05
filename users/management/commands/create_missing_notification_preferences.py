from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import NotificationPreference
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Create missing NotificationPreferences for existing users.'

    def handle(self, *args, **options):
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
