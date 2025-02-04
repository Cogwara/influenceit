from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('recipient__email', 'title', 'message')
    readonly_fields = ('created_at',)

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'email_enabled', 'push_enabled')
    list_filter = ('notification_type', 'email_enabled', 'push_enabled')
    search_fields = ('user__email', 'notification_type')
    raw_id_fields = ('user',)
