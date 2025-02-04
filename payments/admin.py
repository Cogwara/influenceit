from django.contrib import admin
from .models import Payment, PaymentMethod, Invoice

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'is_default', 'created_at')
    list_filter = ('type', 'is_default')
    search_fields = ('user__email',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'payer', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'payer__email')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'payment', 'status', 'due_date', 'created_at')
    list_filter = ('status',)
    search_fields = ('invoice_number', 'payment__transaction_id')
    date_hierarchy = 'created_at'
