from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import NotificationPreference

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates notification preferences for users who don\'t have them'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        created_count = 0

        for user in users:
            _, created = NotificationPreference.objects.get_or_create(
                user=user)
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {
                    created_count} notification preferences'
            )
        )
