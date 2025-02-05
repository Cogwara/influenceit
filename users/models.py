from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import NotificationPreference


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('seeker', 'Brand/Business'),
        ('influencer', 'Influencer'),
        ('brand', 'Brand'),
    )

    user_type = models.CharField(
        max_length=15,
        choices=USER_TYPE_CHOICES,
        default='seeker'
    )
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[MinLengthValidator(10)]
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='profile_pictures/default.png'
    )
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    verification_code_created = models.DateTimeField(null=True, blank=True)

    # Brand/Business specific fields
    company_name = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=50, blank=True)
    company_size = models.CharField(max_length=50, blank=True)

    # Influencer specific fields
    categories = models.JSONField(default=list)
    social_links = models.JSONField(default=dict)
    audience_demographics = models.JSONField(default=dict)
    average_engagement_rate = models.FloatField(default=0.0)
    total_followers = models.IntegerField(default=0)

    is_brand = models.BooleanField(default=False)
    is_influencer = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class UserVerification(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='verification'
    )
    document_type = models.CharField(max_length=50)
    document_file = models.FileField(upload_to='verification_documents/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ),
        default='pending'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Verification for {self.user.email}"


class Niche(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class SocialPlatform(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    url_pattern = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class InfluencerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='influencerprofile'
    )
    bio = models.TextField(blank=True)
    niches = models.ManyToManyField(Niche, related_name='influencers')
    platforms = models.ManyToManyField(
        SocialPlatform, related_name='influencers')
    full_name = models.CharField(max_length=255)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', blank=True, null=True)
    website = models.URLField(blank=True)
    social_links = models.JSONField(blank=True, default=dict)
    followers = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)
    audience_demographics = models.JSONField(blank=True, default=dict)
    audience_interests = models.JSONField(blank=True, default=dict)
    audience_authenticity_score = models.FloatField(default=0.0)
    primary_niche = models.CharField(max_length=100)
    content_types = models.JSONField(blank=True, default=dict)
    brand_collaboration_history = models.JSONField(blank=True, default=dict)
    preferred_payment_model = models.CharField(max_length=100)
    rate_card = models.JSONField(blank=True, default=dict)
    availability = models.CharField(max_length=100)
    post_reach = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    engagement_metrics = models.JSONField(blank=True, default=dict)
    rates = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    metrics = models.JSONField(default=dict, blank=True)
    portfolio = models.ManyToManyField('content.Content')

    def __str__(self):
        return f"Influencer Profile for {self.user.username}"


class SeekerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    social_media_links = models.JSONField(blank=True, default=dict)
    industry = models.CharField(max_length=100)
    target_market = models.JSONField()
    company_size = models.CharField(max_length=100)
    primary_marketing_goals = models.JSONField()
    preferred_influencer_type = models.JSONField()
    campaign_budget_range = models.CharField(max_length=100)
    payment_model = models.CharField(max_length=100)
    team_members = models.JSONField(blank=True, default=dict)
    client_profiles = models.JSONField(blank=True, default=dict)
    social_media_accounts = models.JSONField(blank=True, default=dict)
    utm_links = models.JSONField(blank=True, default=dict)
    tracking_pixels = models.JSONField(blank=True, default=dict)

    def __str__(self):
        return self.brand_name


class InfluencerList(models.Model):
    seeker = models.ForeignKey(SeekerProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    influencers = models.ManyToManyField(InfluencerProfile)


# Notifications App - Handle system notifications
class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_notifications'
    )
    type = models.CharField(max_length=50)
    content = models.JSONField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class BrandProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='brandprofile'
    )
    company_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True)
    industry = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    niches = models.ManyToManyField('discovery.Niche', blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Brand Profile for {self.user.username}"

    @property
    def active_campaigns(self):
        return self.campaign_set.filter(status='active')

    class Meta:
        ordering = ['-created_at']
