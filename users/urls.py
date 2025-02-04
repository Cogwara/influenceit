from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('verify/', views.verify_account, name='verify_account'),
    path('password-reset/',
         views.CustomPasswordResetView.as_view(),
         name='password_reset'),
    path('password-reset/done/',
         views.CustomPasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         views.CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('notifications/', views.update_notification_preferences,
         name='update_notification_preferences'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('settings/', views.settings, name='settings'),
    path('complete-influencer-profile/', views.complete_influencer_profile,
         name='complete_influencer_profile'),
    path('complete-brand-profile/', views.complete_brand_profile,
         name='complete_brand_profile'),
    path('follow/<str:username>/', views.follow_toggle, name='follow_toggle'),
    path('search/', views.search_users, name='search_users'),
]
