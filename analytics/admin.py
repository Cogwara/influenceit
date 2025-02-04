from django.contrib import admin
from .models import (
    PerformanceMetric, CampaignMetric, ContentMetric, 
    InfluencerMetric, AnalyticsSnapshot
)

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('metric_type', 'platform', 'value', 'timestamp')
    list_filter = ('metric_type', 'platform')
    date_hierarchy = 'timestamp'

@admin.register(CampaignMetric)
class CampaignMetricAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'metric_type', 'value', 'timestamp')
    list_filter = ('metric_type',)
    search_fields = ('campaign__title',)
    date_hierarchy = 'timestamp'

@admin.register(ContentMetric)
class ContentMetricAdmin(admin.ModelAdmin):
    list_display = ('content', 'metric_type', 'value', 'timestamp')
    list_filter = ('metric_type',)
    search_fields = ('content__title',)
    date_hierarchy = 'timestamp'

@admin.register(InfluencerMetric)
class InfluencerMetricAdmin(admin.ModelAdmin):
    list_display = ('influencer', 'metric_type', 'platform', 'value', 'timestamp')
    list_filter = ('metric_type', 'platform')
    search_fields = ('influencer__username', 'influencer__email')
    date_hierarchy = 'timestamp'

@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ('date', 'created_at')
    date_hierarchy = 'date'

# Alternatively, you can use the following simpler registration:
# admin.site.register(PerformanceMetric)
