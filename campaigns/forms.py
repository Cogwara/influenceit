from django import forms
from django.forms import widgets
from .models import Campaign, CampaignApplication

class JSONWidget(forms.Textarea):
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'placeholder': '{"key": "value"}',
            'rows': '3'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = [
            'title', 'description', 'categories', 'requirements',
            'deliverables', 'guidelines', 'start_date', 'end_date',
            'budget', 'payment_terms', 'target_audience',
            'required_followers', 'required_engagement_rate'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'deliverables': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'guidelines': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'target_audience': JSONWidget(),
            'required_followers': forms.NumberInput(attrs={'class': 'form-control'}),
            'required_engagement_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean_target_audience(self):
        target_audience = self.cleaned_data.get('target_audience')
        if isinstance(target_audience, str):
            try:
                import json
                return json.loads(target_audience)
            except json.JSONDecodeError:
                raise forms.ValidationError('Please enter valid JSON')
        return target_audience

class CampaignApplicationForm(forms.ModelForm):
    class Meta:
        model = CampaignApplication
        fields = ['proposal', 'proposed_rate', 'portfolio_links', 'notes']
        widgets = {
            'proposal': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'proposed_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'portfolio_links': JSONWidget(),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_portfolio_links(self):
        portfolio_links = self.cleaned_data.get('portfolio_links')
        if isinstance(portfolio_links, str):
            try:
                import json
                return json.loads(portfolio_links)
            except json.JSONDecodeError:
                raise forms.ValidationError('Please enter valid JSON')
        return portfolio_links
