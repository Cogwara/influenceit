from django.contrib import admin
from .models import Content, ContentReview


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'title', 'content_type',
                    'platform', 'status', 'created_at')
    list_filter = ('content_type', 'platform', 'status')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Content Information', {
            'fields': ('contract', 'title', 'content_type', 'platform', 'status')
        }),
        ('Content Details', {
            'fields': ('url', 'caption', 'metrics')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContentReview)
class ContentReviewAdmin(admin.ModelAdmin):
    list_display = ['content', 'reviewer', 'rating', 'status', 'created_at']
    list_filter = ['status', 'rating', 'created_at']
    readonly_fields = ['created_at']
    search_fields = ['content__title', 'reviewer__email', 'feedback']
    fieldsets = (
        (None, {
            'fields': ('content', 'reviewer', 'rating', 'feedback', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
