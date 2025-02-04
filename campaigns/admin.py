from django.contrib import admin
from .models import Campaign, CampaignApplication, CampaignCategory

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'status', 'budget', 'start_date', 'end_date')
    list_filter = ('status', 'categories', 'is_featured')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('categories',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'creator', 'status')
        }),
        ('Campaign Details', {
            'fields': ('categories', 'requirements', 'deliverables', 'guidelines')
        }),
        ('Timeline & Budget', {
            'fields': ('start_date', 'end_date', 'budget', 'payment_terms')
        }),
        ('Metrics', {
            'fields': ('target_audience', 'required_followers', 'required_engagement_rate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CampaignApplication)
class CampaignApplicationAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'influencer', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('campaign__title', 'influencer__email')
    readonly_fields = ('created_at',)

@admin.register(CampaignCategory)
class CampaignCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

# Alternatively, you can use the following simpler registration:
# admin.site.register(Campaign)
