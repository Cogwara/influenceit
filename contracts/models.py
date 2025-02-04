from django.db import models
from django.conf import settings
from campaigns.models import Campaign

# Create your models here.

# Contracts App - Handle agreements and terms


class Contract(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('terminated', 'Terminated')
    )

    # Relationships
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='contracts'
    )
    brand = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='brand_contracts'
    )
    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='influencer_contracts'
    )

    # Contract Details
    contract_number = models.CharField(max_length=50, unique=True)
    terms_and_conditions = models.TextField()
    deliverables = models.JSONField()
    payment_terms = models.JSONField()

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    effective_date = models.DateField()
    expiry_date = models.DateField()

    # Status and Amount
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    contract_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Optional fields
    notes = models.TextField(blank=True)
    signed_by_brand = models.DateTimeField(null=True, blank=True)
    signed_by_influencer = models.DateTimeField(null=True, blank=True)

    title = models.CharField(max_length=255)

    def __str__(self):
        return f"Contract #{self.contract_number}"

    def save(self, *args, **kwargs):
        if not self.contract_number:
            # Generate contract number (you can customize this format)
            last_contract = Contract.objects.order_by('-created_at').first()
            if last_contract:
                last_number = int(last_contract.contract_number[4:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.contract_number = f'CTR-{new_number:06d}'
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class ContractTemplate(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
