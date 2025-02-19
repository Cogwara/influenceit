from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import CustomUser, InfluencerProfile, SeekerProfile, InfluencerList, UserVerification, BrandProfile
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'user_type', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        return email


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')


class InfluencerProfileForm(forms.ModelForm):
    class Meta:
        model = InfluencerProfile
        fields = ('full_name', 'profile_picture', 'bio', 'website', 'social_links', 'followers',
                  'engagement_rate', 'audience_demographics', 'audience_interests',
                  'audience_authenticity_score', 'primary_niche', 'content_types',
                  'brand_collaboration_history', 'preferred_payment_model', 'rate_card',
                  'availability', 'post_reach', 'impressions', 'engagement_metrics')


class SeekerProfileForm(forms.ModelForm):
    class Meta:
        model = SeekerProfile
        fields = ('brand_name', 'logo', 'website', 'social_media_links', 'industry',
                  'target_market', 'company_size', 'primary_marketing_goals',
                  'preferred_influencer_type', 'campaign_budget_range', 'payment_model',
                  'team_members', 'client_profiles', 'social_media_accounts', 'utm_links',
                  'tracking_pixels')


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name',
                  'last_name']  # Exclude 'date_joined'


class InfluencerListForm(forms.ModelForm):
    class Meta:
        model = InfluencerList
        fields = ['name', 'influencers']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'profile_picture', 'bio',
            'location', 'website', 'phone_number'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class BrandProfileForm(forms.ModelForm):
    class Meta:
        model = BrandProfile
        fields = [
            'company_name',
            'logo',
            'description',
            'website',
            'industry',
            'location',
            'niches',
            'founded_year',
            'company_size'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'niches': forms.CheckboxSelectMultiple(),
            'founded_year': forms.NumberInput(attrs={'min': 1900, 'max': 2024}),
            'company_size': forms.Select(choices=[
                ('1-10', '1-10 employees'),
                ('11-50', '11-50 employees'),
                ('51-200', '51-200 employees'),
                ('201-500', '201-500 employees'),
                ('501+', '501+ employees')
            ])
        }


class InfluencerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['categories', 'social_links', 'audience_demographics']

    def clean_social_links(self):
        social_links = self.cleaned_data.get('social_links')
        required_platforms = ['instagram', 'youtube', 'tiktok']

        for platform in required_platforms:
            if platform not in social_links:
                raise forms.ValidationError(
                    f"Please provide your {platform.title()} profile link"
                )
        return social_links


class VerificationForm(forms.ModelForm):
    class Meta:
        model = UserVerification
        fields = ['document_type', 'document_file']
        widgets = {
            'document_file': forms.FileInput(attrs={
                'accept': '.pdf,.jpg,.jpeg,.png'
            })
        }

    def clean_document_file(self):
        file = self.cleaned_data.get('document_file')
        if file:
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be under 5MB")
        return file


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'bio',
            'location',
            'website',
            'profile_picture'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']


class ProfilePhotoForm(forms.Form):
    photo = forms.ImageField(
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("The new passwords don't match")
        return cleaned_data
