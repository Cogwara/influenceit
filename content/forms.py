from django import forms
from .models import Content, ContentReview
from contracts.models import Contract  # Import Contract from contracts app

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['contract', 'title', 'description', 'content_type', 
                 'content_url', 'platform', 'status', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'content_type': forms.Select(attrs={'class': 'form-control'}),
            'content_url': forms.URLInput(attrs={'class': 'form-control'}),
            'platform': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contract': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filter contracts based on user role
            if user.is_brand:
                self.fields['contract'].queryset = Contract.objects.filter(brand=user)
            else:
                self.fields['contract'].queryset = Contract.objects.filter(influencer=user)

    def clean_url(self):
        url = self.cleaned_data.get('url')
        content_type = self.cleaned_data.get('type')
        
        # Validate URL based on content type
        if content_type == 'instagram':
            if 'instagram.com' not in url:
                raise forms.ValidationError("Please enter a valid Instagram URL")
        elif content_type == 'youtube':
            if 'youtube.com' not in url and 'youtu.be' not in url:
                raise forms.ValidationError("Please enter a valid YouTube URL")
        elif content_type == 'tiktok':
            if 'tiktok.com' not in url:
                raise forms.ValidationError("Please enter a valid TikTok URL")
        
        return url

class ContentReviewForm(forms.ModelForm):
    class Meta:
        model = ContentReview
        fields = ['feedback', 'status']
        widgets = {
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your feedback'
            }),
            'status': forms.Select(attrs={'class': 'form-select'})
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        feedback = cleaned_data.get('feedback')
        
        if status == 'rejected' and not feedback:
            raise forms.ValidationError(
                "Please provide feedback when rejecting content"
            )
        
        return cleaned_data 