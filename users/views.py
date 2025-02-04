from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CustomUserChangeForm, InfluencerListForm, InfluencerProfileForm, SeekerProfileForm, CustomAuthenticationForm, ProfileUpdateForm, BrandProfileForm, VerificationForm, UserProfileForm
from .models import CustomUser, InfluencerProfile, SeekerProfile, UserVerification
from campaigns.models import Campaign
from django.contrib.auth.views import (
    LoginView, LogoutView, 
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from notifications.models import NotificationPreference
from django.db import transaction


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create an InfluencerProfile or SeekerProfile for the new user with default values
            if user.user_type == 'influencer':
                InfluencerProfile.objects.create(
                    user=user,
                    full_name='',
                    profile_picture=None,
                    bio='',
                    website='',
                    social_links={},
                    followers=0,
                    engagement_rate=0.0,
                    audience_demographics={},
                    audience_interests={},
                    audience_authenticity_score=0.0,
                    primary_niche='',
                    content_types={},
                    brand_collaboration_history={},
                    preferred_payment_model='',
                    rate_card={},
                    availability='',
                    post_reach=0,
                    impressions=0,
                    engagement_metrics={}
                )
            elif user.user_type == 'seeker':
                SeekerProfile.objects.create(
                    user=user,
                    brand_name='',
                    logo=None,
                    website='',
                    social_media_links={},
                    industry='',
                    target_market={},
                    company_size='',
                    primary_marketing_goals={},
                    preferred_influencer_type={},
                    campaign_budget_range='',
                    payment_model='',
                    team_members={},
                    client_profiles={},
                    social_media_accounts={},
                    utm_links={},
                    tracking_pixels={}
                )
            login(request, user)
            # Pass the username argument
            return redirect('users:profile', username=user.username)
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})


@login_required
def profile_view(request, username):
    user = get_object_or_404(CustomUser, username=username)
    if user.user_type == 'influencer':
        profile = get_object_or_404(InfluencerProfile, user=user)
        return render(request, 'users/influencer_profile.html', {'user': user, 'profile': profile})
    else:
        profile = get_object_or_404(SeekerProfile, user=user)
        campaigns = Campaign.objects.filter(created_by=user)
        return render(request, 'users/seeker_profile.html', {'user': user, 'profile': profile, 'campaigns': campaigns})


@login_required
def update_profile(request):
    user = request.user
    if user.user_type == 'influencer':
        profile = get_object_or_404(InfluencerProfile, user=user)
        profile_form_class = InfluencerProfileForm
    else:
        profile = get_object_or_404(SeekerProfile, user=user)
        profile_form_class = SeekerProfileForm

    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=user)
        profile_form = profile_form_class(
            request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('users:profile', username=user.username)
    else:
        user_form = CustomUserChangeForm(instance=user)
        profile_form = profile_form_class(instance=profile)

    return render(request, 'users/update_profile.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def create_influencer_list(request):
    if request.method == 'POST':
        form = InfluencerListForm(request.POST)
        if form.is_valid():
            influencer_list = form.save(commit=False)
            influencer_list.seeker = request.user.seekerprofile
            influencer_list.save()
            form.save_m2m()
            return redirect('users:profile', username=request.user.username)
    else:
        form = InfluencerListForm()
    return render(request, 'users/create_influencer_list.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Pass the username argument
                return redirect('users:profile', username=user.username)
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('index')


def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('users:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return get_object_or_404(
            CustomUser,
            username=self.kwargs.get('username')
        )


@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if request.user.user_type == 'seeker':
            specific_form = BrandProfileForm(
                request.POST,
                instance=request.user
            )
        else:
            specific_form = InfluencerProfileForm(
                request.POST,
                instance=request.user
            )

        if profile_form.is_valid() and specific_form.is_valid():
            profile_form.save()
            specific_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile', username=request.user.username)
    else:
        profile_form = ProfileUpdateForm(instance=request.user)
        if request.user.user_type == 'seeker':
            specific_form = BrandProfileForm(instance=request.user)
        else:
            specific_form = InfluencerProfileForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {
        'profile_form': profile_form,
        'specific_form': specific_form
    })


@login_required
def verify_account(request):
    try:
        verification = request.user.verification
    except UserVerification.DoesNotExist:
        verification = None

    if request.method == 'POST':
        if not verification:
            form = VerificationForm(request.POST, request.FILES)
            if form.is_valid():
                verification = form.save(commit=False)
                verification.user = request.user
                verification.save()
                messages.success(
                    request,
                    'Verification documents submitted successfully!'
                )
                return redirect('users:profile', username=request.user.username)
        else:
            messages.warning(
                request,
                'You have already submitted verification documents.'
            )
    else:
        form = VerificationForm()

    return render(request, 'users/verify_account.html', {
        'form': form,
        'verification': verification
    })


@login_required
def update_social_links(request):
    if request.method == 'POST':
        user = request.user
        social_links = request.POST.dict()
        social_links.pop('csrfmiddlewaretoken', None)
        
        user.social_links = social_links
        user.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def update_demographics(request):
    if request.method == 'POST':
        user = request.user
        demographics = request.POST.dict()
        demographics.pop('csrfmiddlewaretoken', None)
        
        user.audience_demographics = demographics
        user.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('core:home')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = 'core:home'


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


@login_required
def update_notification_preferences(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get all current preferences
                current_preferences = list(NotificationPreference.objects.filter(user=request.user))
                
                # Create a list to store updated preferences
                updated_preferences = []
                
                # Update each preference based on form data
                for pref in current_preferences:
                    email_enabled = request.POST.get(f'email_{pref.notification_type}') == 'on'
                    push_enabled = request.POST.get(f'push_{pref.notification_type}') == 'on'
                    
                    # Create new preference object with updated values
                    updated_pref = NotificationPreference(
                        user=request.user,
                        notification_type=pref.notification_type,
                        email_enabled=email_enabled,
                        push_enabled=push_enabled
                    )
                    updated_preferences.append(updated_pref)
                
                # Delete existing preferences
                NotificationPreference.objects.filter(user=request.user).delete()
                
                # Create new preferences
                NotificationPreference.objects.bulk_create(updated_preferences)
                
                messages.success(request, 'Notification preferences updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating preferences: {str(e)}')
        
        return redirect('users:notification_preferences')

    # Get current preferences for display
    preferences = NotificationPreference.objects.filter(user=request.user)
    return render(request, 'users/notification_preferences.html', {
        'preferences': preferences
    })
