# Generated by Django 5.1.5 on 2025-02-04 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_alter_notificationpreference_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationpreference',
            name='notification_type',
            field=models.CharField(choices=[('email', 'Email'), ('push', 'Push Notification'), ('both', 'Both'), ('none', 'None')], default='email', max_length=10),
        ),
    ]
