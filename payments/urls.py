from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('success/', views.payment_success, name='success'),
    path('error/', views.payment_error, name='error'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe-webhook'),
    path('history/', views.payment_history, name='history'),
    path('detail/<int:pk>/', views.payment_detail, name='detail'),
] 