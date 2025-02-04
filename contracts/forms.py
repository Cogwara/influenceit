from django import forms
from django.forms import widgets
from .models import Contract, ContractTemplate

class JSONWidget(forms.Textarea):
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'rows': '3'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'campaign', 'terms_and_conditions', 'deliverables',
            'payment_terms', 'effective_date', 'expiry_date',
            'contract_value', 'notes', 'status'
        ]
        widgets = {
            'campaign': forms.Select(attrs={'class': 'form-control'}),
            'terms_and_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'deliverables': JSONWidget(attrs={
                'placeholder': '''{
    "content_type": "video",
    "quantity": 3,
    "requirements": ["1080p minimum", "30s duration"],
    "platforms": ["Instagram", "TikTok"]
}'''
            }),
            'payment_terms': JSONWidget(attrs={
                'placeholder': '''{
    "milestone1": {"amount": 500, "description": "Upon signing", "due_date": "2024-03-01"},
    "milestone2": {"amount": 500, "description": "Upon completion", "due_date": "2024-04-01"}
}'''
            }),
            'effective_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'contract_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        effective_date = cleaned_data.get('effective_date')
        expiry_date = cleaned_data.get('expiry_date')

        if effective_date and expiry_date and effective_date > expiry_date:
            raise forms.ValidationError(
                "Effective date cannot be later than expiry date."
            )

        return cleaned_data

    def clean_deliverables(self):
        """Validate and convert deliverables JSON."""
        deliverables = self.cleaned_data.get('deliverables')
        if isinstance(deliverables, str):
            try:
                import json
                return json.loads(deliverables)
            except json.JSONDecodeError:
                raise forms.ValidationError('Please enter valid JSON for deliverables')
        return deliverables

    def clean_payment_terms(self):
        """Validate and convert payment_terms JSON."""
        payment_terms = self.cleaned_data.get('payment_terms')
        if isinstance(payment_terms, str):
            try:
                import json
                return json.loads(payment_terms)
            except json.JSONDecodeError:
                raise forms.ValidationError('Please enter valid JSON for payment terms')
        return payment_terms

class ContractTemplateForm(forms.ModelForm):
    class Meta:
        model = ContractTemplate
        fields = ['name', 'content']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Template name'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Enter template content...'
            })
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        required_variables = ['{campaign_name}', '{brand_name}', '{influencer_name}']
        
        for var in required_variables:
            if var not in content:
                raise forms.ValidationError(f"Template must include {var} variable.")
        
        return content 