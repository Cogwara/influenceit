from django.contrib import admin
from .models import Contract, ContractTemplate

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'brand', 'influencer', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('contract_number', 'brand__email', 'influencer__email')
    readonly_fields = ('contract_number', 'signed_date', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contract Information', {
            'fields': ('contract_number', 'brand', 'influencer', 'status', 'terms')
        }),
        ('Payment Information', {
            'fields': ('payment_schedule',)
        }),
        ('Signatures', {
            'fields': ('brand_signature', 'influencer_signature', 'signed_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'updated_at')
    list_filter = ('creator',)
    search_fields = ('title', 'content')
    readonly_fields = ('updated_at',)
