from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('', views.CampaignListView.as_view(), name='list'),
    path('create/', views.CampaignCreateView.as_view(), name='create'),
    path('<int:pk>/', views.CampaignDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.CampaignUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.CampaignDeleteView.as_view(), name='delete'),
    path('<int:pk>/apply/', views.apply_to_campaign, name='apply'),
    path('<int:pk>/applications/', views.manage_applications, name='manage_applications'),
    path('application/<int:pk>/update/', views.update_application_status, name='update_application'),
    path('search/', views.search_campaigns, name='search'),
    path('categories/<str:category>/', views.CategoryCampaignListView.as_view(), name='category'),
]
