from django import forms
from .models import SearchFilter, InfluencerList

class SearchFilterForm(forms.ModelForm):
    class Meta:
        model = SearchFilter
        exclude = ['user']
        widgets = {
            'criteria': forms.HiddenInput()
        }

    niche = forms.MultipleChoiceField(
        choices=NICHE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    platform = forms.MultipleChoiceField(
        choices=PLATFORM_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    followers_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Minimum followers'})
    )
    
    engagement_rate_min = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Minimum engagement rate'})
    )

class InfluencerListForm(forms.ModelForm):
    class Meta:
        model = InfluencerList
        exclude = ['creator', 'influencers']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'List name'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Add notes about this list'})
        } 