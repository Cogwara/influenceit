# Generated by Django 5.1.5 on 2025-02-04 15:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('campaign', 'Campaign'), ('message', 'Message'), ('follower', 'New Follower'), ('mention', 'Mention'), ('update', 'Platform Update')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('link', models.URLField(blank=True)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='system_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_notifications', models.BooleanField(default=True)),
                ('push_notifications', models.BooleanField(default=True)),
                ('new_campaign_notifications', models.BooleanField(default=True)),
                ('campaign_updates', models.BooleanField(default=True)),
                ('campaign_deadlines', models.BooleanField(default=True)),
                ('new_message_notifications', models.BooleanField(default=True)),
                ('message_replies', models.BooleanField(default=True)),
                ('new_follower_notifications', models.BooleanField(default=True)),
                ('profile_mentions', models.BooleanField(default=True)),
                ('platform_updates', models.BooleanField(default=True)),
                ('newsletter', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification Preference',
                'verbose_name_plural': 'Notification Preferences',
            },
        ),
    ]
