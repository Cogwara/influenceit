from django import forms
from .models import SearchFilter, InfluencerList, Category, Niche


class SearchFilterForm(forms.Form):
    FOLLOWER_RANGE_CHOICES = [
        ('', 'Any followers'),
        ('0-10k', '0-10K'),
        ('10k-50k', '10K-50K'),
        ('50k-100k', '50K-100K'),
        ('100k-500k', '100K-500K'),
        ('500k+', '500K+'),
    ]

    ENGAGEMENT_RATE_CHOICES = [
        ('', 'Any engagement rate'),
        ('0-1', '0-1%'),
        ('1-3', '1-3%'),
        ('3-5', '3-5%'),
        ('5-10', '5-10%'),
        ('10+', '10%+'),
    ]

    # Search and basic filters
    search_query = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search influencers...',
        'class': 'form-control'
    }))

    niche = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    follower_range = forms.ChoiceField(
        choices=[('', 'Any followers')] + FOLLOWER_RANGE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    engagement_rate = forms.ChoiceField(
        choices=[('', 'Any engagement')] + ENGAGEMENT_RATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Location filters
    country = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Save filter
    save_filter = forms.BooleanField(required=False)
    filter_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Name this filter',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set niche choices when form is instantiated
        self.fields['niche'].choices = [('', 'All Niches')] + [
            (niche.id, niche.name) for niche in Niche.objects.all()
        ]

    def clean(self):
        cleaned_data = super().clean()
        save_filter = cleaned_data.get('save_filter')
        filter_name = cleaned_data.get('filter_name')

        if save_filter and not filter_name:
            raise forms.ValidationError(
                "Please provide a name for the filter if you want to save it."
            )

        return cleaned_data


class InfluencerListForm(forms.ModelForm):
    class Meta:
        model = InfluencerList
        exclude = ['creator', 'influencers']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'List name'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Add notes about this list'})
        }
