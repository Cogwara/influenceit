from django.db import models
from django.conf import settings
from django.utils.text import slugify
from influenceit import settings
from users.models import SeekerProfile, InfluencerProfile


class CampaignCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Campaign Categories'


class Campaign(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_campaigns'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    categories = models.ManyToManyField(CampaignCategory)
    requirements = models.TextField()
    deliverables = models.TextField()
    guidelines = models.TextField()
    
    # Timeline and Budget
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    payment_terms = models.TextField()
    
    # Campaign Details
    target_audience = models.JSONField(default=dict)
    required_followers = models.IntegerField(default=0)
    required_engagement_rate = models.FloatField(default=0.0)
    
    # Status and Timestamps
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class CampaignApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn')
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='campaign_applications'
    )
    proposal = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields for application details
    proposed_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    portfolio_links = models.JSONField(default=list)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.influencer} - {self.campaign}"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['campaign', 'influencer']
