from django.db import models
from django.conf import settings
from django.utils import timezone
from contracts.models import Contract

# Create your models here.

# Payments App - Handle financial transactions
class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    stripe_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']

class PaymentMethod(models.Model):
    TYPE_CHOICES = (
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Account'),
        ('paypal', 'PayPal'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_default = models.BooleanField(default=False)
    
    # For cards
    card_last4 = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    card_exp_month = models.IntegerField(null=True, blank=True)
    card_exp_year = models.IntegerField(null=True, blank=True)
    
    # For bank accounts
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_last4 = models.CharField(max_length=4, blank=True)
    
    # For PayPal
    paypal_email = models.EmailField(blank=True)
    
    # Common fields
    stripe_payment_method_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.user.email}"

    class Meta:
        ordering = ['-is_default', '-created_at']

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue')
    )

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='invoice'
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # Invoice details
    due_date = models.DateField()
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    
    # Additional charges
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # PDF storage
    pdf_file = models.FileField(
        upload_to='invoices/',
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number (you can customize this format)
            last_invoice = Invoice.objects.order_by('-created_at').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.invoice_number = f'INV{new_number:06d}'
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
