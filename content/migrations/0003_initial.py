# Generated by Django 5.1.5 on 2025-02-04 14:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('content', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_content', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contentreview',
            name='content',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content.content'),
        ),
        migrations.AddField(
            model_name='contentreview',
            name='reviewer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
