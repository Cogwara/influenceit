from django.db import models
from django.conf import settings
from campaigns.models import Campaign
from content.models import Content

class BaseMetric(models.Model):
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class PerformanceMetric(BaseMetric):
    METRIC_TYPES = (
        ('engagement_rate', 'Engagement Rate'),
        ('reach', 'Reach'),
        ('impressions', 'Impressions'),
        ('clicks', 'Clicks'),
        ('conversions', 'Conversions'),
        ('roi', 'ROI'),
    )

    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    platform = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['-timestamp']

class CampaignMetric(BaseMetric):
    METRIC_TYPES = (
        ('total_reach', 'Total Reach'),
        ('total_impressions', 'Total Impressions'),
        ('total_engagement', 'Total Engagement'),
        ('conversion_rate', 'Conversion Rate'),
        ('cost_per_engagement', 'Cost per Engagement'),
        ('roi', 'Return on Investment'),
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    
    class Meta:
        ordering = ['-timestamp']
        unique_together = ['campaign', 'metric_type', 'timestamp']

    def __str__(self):
        return f"{self.campaign.title} - {self.get_metric_type_display()}"

class ContentMetric(BaseMetric):
    METRIC_TYPES = (
        ('views', 'Views'),
        ('likes', 'Likes'),
        ('comments', 'Comments'),
        ('shares', 'Shares'),
        ('saves', 'Saves'),
        ('engagement_rate', 'Engagement Rate'),
    )

    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    platform_data = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-timestamp']
        unique_together = ['content', 'metric_type', 'timestamp']

    def __str__(self):
        return f"{self.content} - {self.get_metric_type_display()}"

class InfluencerMetric(BaseMetric):
    METRIC_TYPES = (
        ('followers', 'Followers'),
        ('avg_engagement_rate', 'Average Engagement Rate'),
        ('total_reach', 'Total Reach'),
        ('content_performance', 'Content Performance'),
        ('campaign_success_rate', 'Campaign Success Rate'),
    )

    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    platform = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['-timestamp']
        unique_together = ['influencer', 'metric_type', 'platform', 'timestamp']

    def __str__(self):
        return f"{self.influencer.username} - {self.get_metric_type_display()}"

class AnalyticsSnapshot(models.Model):
    date = models.DateField(unique=True)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Analytics Snapshot - {self.date}"
