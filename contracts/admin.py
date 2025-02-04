from django.contrib import admin
from .models import Contract, ContractTemplate


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at']
    list_filter = ['status']
    readonly_fields = ['created_at']
    search_fields = ['title']


@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    # Change 'title' to 'name' if that's your field name
    list_display = ['name', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']  # Remove 'updated_at'
    search_fields = ['name']
