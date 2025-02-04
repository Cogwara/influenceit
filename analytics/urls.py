from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('campaigns/', views.campaign_analytics, name='campaign_analytics'),
    path('content/', views.content_analytics, name='content_analytics'),
    path('performance/', views.performance_analytics, name='performance_analytics'),
    path('export/', views.export_analytics, name='export_analytics'),
    path('metrics/<str:metric_type>/', views.get_metrics, name='get_metrics'),
]
