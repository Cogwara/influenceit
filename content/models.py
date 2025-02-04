from django.db import models
from django.conf import settings
from contracts.models import Contract  # Import Contract from contracts app

# Create your models here.

# Content App - Handle content management


class Content(models.Model):
    CONTENT_TYPE_CHOICES = (
        ('video', 'Video'),
        ('image', 'Image'),
        ('text', 'Text'),
        ('story', 'Story'),
        ('reel', 'Reel'),
    )

    PLATFORM_CHOICES = (
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('published', 'Published'),
    )

    # Relationships
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_content'
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='content'
    )

    # Content Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES
    )
    content_url = models.URLField()
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    notes = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # Analytics
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Content'
        verbose_name_plural = 'Content'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('content:detail', kwargs={'pk': self.pk})

    def update_analytics(self, views=0, likes=0, shares=0, comments=0):
        """Update content analytics."""
        self.views += views
        self.likes += likes
        self.shares += shares
        self.comments += comments
        self.save()

    @property
    def total_engagement(self):
        """Calculate total engagement."""
        return self.likes + self.shares + self.comments

    @property
    def engagement_rate(self):
        """Calculate engagement rate."""
        if self.views > 0:
            return (self.total_engagement / self.views) * 100
        return 0


class ContentReview(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )

    content = models.ForeignKey('Content', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()
    feedback = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.content} by {self.reviewer}"

    class Meta:
        ordering = ['-created_at']
