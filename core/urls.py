from django.urls import path
from .views import HomeView, AboutView, ContactView, FAQView, TermsView, PrivacyView, newsletter_signup

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('terms/', TermsView.as_view(), name='terms'),
    path('privacy/', PrivacyView.as_view(), name='privacy'),
    path('newsletter_signup/', newsletter_signup, name='newsletter_signup'),
]
