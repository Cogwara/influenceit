# Generated by Django 5.1.5 on 2025-02-05 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='influencerprofile',
            name='rates',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
