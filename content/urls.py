from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('', views.ContentListView.as_view(), name='list'),
    path('<int:pk>/', views.ContentDetailView.as_view(), name='detail'),
    path('create/', views.ContentCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.ContentUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ContentDeleteView.as_view(), name='delete'),
    path('<int:pk>/approve/', views.approve_content, name='approve'),
    path('<int:pk>/reject/', views.reject_content, name='reject'),
    path('<int:pk>/review/', views.review_content, name='review'),
    path('<int:pk>/metrics/', views.update_metrics, name='update_metrics'),
    path('<int:pk>/analytics/', views.content_analytics, name='analytics'),
] 