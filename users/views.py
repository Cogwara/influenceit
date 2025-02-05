from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from .forms import (
    UserRegistrationForm,
    UserUpdateForm,
    ProfileUpdateForm,
    InfluencerProfileForm,
    BrandProfileForm
)
from .models import CustomUser, InfluencerProfile, BrandProfile
from notifications.models import NotificationPreference


def register(request):
    """Handle user registration for both influencers and brands"""
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Signals handle profile and preferences
            login(request, user)
            messages.success(
                request, 'Registration successful! Please complete your profile.')

            # Redirect based on user type
            if user.user_type == 'influencer':
                return redirect('users:complete_influencer_profile')
            elif user.user_type in ['brand', 'seeker']:
                return redirect('users:complete_brand_profile')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def complete_influencer_profile(request):
    """Complete profile setup for influencers"""
    if hasattr(request.user, 'influencerprofile'):
        return redirect('users:profile')

    if request.method == 'POST':
        form = InfluencerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(
                request, 'Your profile has been created successfully!')
            return redirect('users:profile')
    else:
        form = InfluencerProfileForm()

    return render(request, 'users/complete_influencer_profile.html', {'form': form})


@login_required
def complete_brand_profile(request):
    """Complete profile setup for brands"""
    if hasattr(request.user, 'brandprofile'):
        return redirect('users:profile')

    if request.method == 'POST':
        form = BrandProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(
                request, 'Your brand profile has been created successfully!')
            return redirect('users:profile')
    else:
        form = BrandProfileForm()

    return render(request, 'users/complete_brand_profile.html', {'form': form})


@login_required
def profile(request):
    """Display and update user profile"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)

        # Choose the correct profile form based on user type
        if request.user.user_type == 'influencer':
            profile_form = InfluencerProfileForm(
                request.POST,
                request.FILES,
                instance=request.user.influencerprofile
            )
        else:
            profile_form = BrandProfileForm(
                request.POST,
                request.FILES,
                instance=request.user.brandprofile
            )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(
                request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        if request.user.user_type == 'influencer':
            profile_form = InfluencerProfileForm(
                instance=request.user.influencerprofile)
        else:
            profile_form = BrandProfileForm(instance=request.user.brandprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_view(request, username):
    """Public view of a user's profile"""
    user = get_object_or_404(CustomUser, username=username)

    if user.user_type == 'influencer':
        profile = get_object_or_404(InfluencerProfile, user=user)
        template = 'users/influencer_profile.html'
    else:
        profile = get_object_or_404(BrandProfile, user=user)
        template = 'users/brand_profile.html'

    context = {
        'profile_user': user,
        'profile': profile
    }
    return render(request, template, context)


@login_required
def follow_toggle(request, username):
    """Handle following/unfollowing users"""
    if request.method == 'POST':
        user_to_follow = get_object_or_404(CustomUser, username=username)

        if request.user == user_to_follow:
            return JsonResponse({'error': 'You cannot follow yourself'}, status=400)

        if request.user in user_to_follow.followers.all():
            user_to_follow.followers.remove(request.user)
            is_following = False
        else:
            user_to_follow.followers.add(request.user)
            is_following = True

        return JsonResponse({
            'is_following': is_following,
            'followers_count': user_to_follow.followers.count()
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def settings(request):
    """User settings page"""
    notification_prefs, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        # Update each preference field directly
        notification_prefs.email_notifications = request.POST.get(
            'email_notifications') == 'on'
        notification_prefs.push_notifications = request.POST.get(
            'push_notifications') == 'on'
        notification_prefs.new_campaign_notifications = request.POST.get(
            'new_campaign_notifications') == 'on'
        notification_prefs.campaign_updates = request.POST.get(
            'campaign_updates') == 'on'
        notification_prefs.campaign_deadlines = request.POST.get(
            'campaign_deadlines') == 'on'
        notification_prefs.new_message_notifications = request.POST.get(
            'new_message_notifications') == 'on'
        notification_prefs.message_replies = request.POST.get(
            'message_replies') == 'on'
        notification_prefs.new_follower_notifications = request.POST.get(
            'new_follower_notifications') == 'on'
        notification_prefs.profile_mentions = request.POST.get(
            'profile_mentions') == 'on'
        notification_prefs.platform_updates = request.POST.get(
            'platform_updates') == 'on'
        notification_prefs.newsletter = request.POST.get('newsletter') == 'on'

        notification_prefs.save()
        messages.success(
            request, 'Your settings have been updated successfully!')
        return redirect('users:settings')

    return render(request, 'users/settings.html', {
        'notification_prefs': notification_prefs
    })


def search_users(request):
    """Search for users (AJAX endpoint)"""
    query = request.GET.get('q', '')
    user_type = request.GET.get('type', 'all')

    users = CustomUser.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )

    if user_type != 'all':
        users = users.filter(user_type=user_type)

    users = users[:10]  # Limit results

    results = [{
        'username': user.username,
        'name': user.get_full_name(),
        'profile_url': reverse('users:profile_view', args=[user.username]),
        'avatar_url': user.get_avatar_url()
    } for user in users]

    return JsonResponse({'results': results})


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('core:home')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            # Session expires when browser closes
            self.request.session.set_expiry(0)

        # Call parent class's form_valid() to complete login process
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {
                         self.request.user.username}!')
        return response


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('core:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been successfully logged out.')
        response = super().dispatch(request, *args, **kwargs)
        return response


@login_required
def edit_profile(request):
    """Handle profile editing for both influencers and brands"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)

        # Select the appropriate profile form based on user type
        if request.user.user_type == 'influencer':
            profile_form = InfluencerProfileForm(
                request.POST,
                request.FILES,
                instance=request.user.influencerprofile
            )
        else:
            profile_form = BrandProfileForm(
                request.POST,
                request.FILES,
                instance=request.user.brandprofile
            )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)

            # Handle profile photo/logo upload
            if 'profile_photo' in request.FILES:
                if request.user.user_type == 'influencer':
                    profile.profile_photo = request.FILES['profile_photo']
                else:
                    profile.logo = request.FILES['profile_photo']

            profile.save()
            profile_form.save_m2m()  # Save many-to-many relationships

            messages.success(
                request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)

        # Get the appropriate profile instance and form
        if request.user.user_type == 'influencer':
            profile_form = InfluencerProfileForm(
                instance=request.user.influencerprofile)
        else:
            profile_form = BrandProfileForm(instance=request.user.brandprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_type': request.user.user_type
    }

    return render(request, 'users/edit_profile.html', context)


@login_required
def verify_account(request):
    """Handle account verification process"""
    user = request.user

    # Check if user is already verified
    if user.is_verified:
        messages.info(request, 'Your account is already verified.')
        return redirect('users:profile')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'request':
            # Generate verification code
            verification_code = get_random_string(
                length=6, allowed_chars='0123456789')
            user.verification_code = verification_code
            user.verification_code_created = timezone.now()
            user.save()

            # Send verification email
            context = {
                'user': user,
                'verification_code': verification_code,
                'valid_hours': 24  # Code validity period
            }

            html_message = render_to_string(
                'users/emails/verification_email.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                'Verify Your Account',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(
                request, 'Verification code has been sent to your email.')
            return redirect('users:verify_account')

        elif action == 'verify':
            submitted_code = request.POST.get('verification_code')

            # Check if verification code exists and is valid
            if not user.verification_code:
                messages.error(
                    request, 'Please request a new verification code.')
                return redirect('users:verify_account')

            # Check if code has expired (24 hours)
            if user.verification_code_created < timezone.now() - timedelta(hours=24):
                messages.error(
                    request, 'Verification code has expired. Please request a new one.')
                return redirect('users:verify_account')

            # Verify the code
            if submitted_code == user.verification_code:
                user.is_verified = True
                user.verification_code = None
                user.verification_code_created = None
                user.save()

                messages.success(
                    request, 'Your account has been successfully verified!')
                return redirect('users:profile')
            else:
                messages.error(
                    request, 'Invalid verification code. Please try again.')

    return render(request, 'users/verify_account.html', {
        'has_active_code': bool(user.verification_code and
                                user.verification_code_created > timezone.now() - timedelta(hours=24))
    })


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/emails/password_reset_email.html'
    subject_template_name = 'users/emails/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')

    def form_valid(self, form):
        """Add success message and handle invalid email"""
        email = form.cleaned_data.get('email')
        users = self.get_users(email)
        if not len(list(users)):
            messages.error(
                self.request, 'No account found with this email address.')
            return self.form_invalid(form)
        messages.success(
            self.request, 'Password reset instructions have been sent to your email.')
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')

    def form_valid(self, form):
        messages.success(
            self.request, 'Your password has been successfully reset.')
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


@login_required
def update_notification_preferences(request):
    """Handle updating user notification preferences"""
    try:
        # Get or create notification preferences for the user
        notification_prefs, created = NotificationPreference.objects.get_or_create(
            user=request.user
        )

        if request.method == 'POST':
            # Update each preference field directly
            notification_prefs.email_notifications = request.POST.get(
                'email_notifications') == 'on'
            notification_prefs.push_notifications = request.POST.get(
                'push_notifications') == 'on'
            notification_prefs.new_campaign_notifications = request.POST.get(
                'new_campaign_notifications') == 'on'
            notification_prefs.campaign_updates = request.POST.get(
                'campaign_updates') == 'on'
            notification_prefs.campaign_deadlines = request.POST.get(
                'campaign_deadlines') == 'on'
            notification_prefs.new_message_notifications = request.POST.get(
                'new_message_notifications') == 'on'
            notification_prefs.message_replies = request.POST.get(
                'message_replies') == 'on'
            notification_prefs.new_follower_notifications = request.POST.get(
                'new_follower_notifications') == 'on'
            notification_prefs.profile_mentions = request.POST.get(
                'profile_mentions') == 'on'
            notification_prefs.platform_updates = request.POST.get(
                'platform_updates') == 'on'
            notification_prefs.newsletter = request.POST.get(
                'newsletter') == 'on'

            notification_prefs.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})

            messages.success(
                request, 'Notification preferences updated successfully!')
            return redirect('users:settings')

        context = {
            'notification_prefs': notification_prefs,
        }
        return render(request, 'users/notification_preferences.html', context)

    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        messages.error(
            request, 'An error occurred while updating notification preferences.')
        return redirect('users:settings')


@login_required
def user_profile(request):
    user = request.user
    profile = None

    try:
        if user.user_type == 'influencer':
            profile = user.influencerprofile
        elif user.user_type in ['brand', 'seeker']:
            profile = user.brandprofile
    except ObjectDoesNotExist:
        # Redirect to profile creation page
        messages.error(
            request, 'Profile not found. Please create your profile.')
        if user.user_type == 'influencer':
            return redirect('users:create_influencer_profile')
        elif user.user_type in ['brand', 'seeker']:
            return redirect('users:create_brand_profile')

    return render(request, 'users/profile.html', {'profile': profile})
