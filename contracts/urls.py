from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.contract_list, name='list'),
    path('create/', views.create_contract, name='create'),
    path('<int:pk>/', views.contract_detail, name='detail'),
    path('<int:pk>/edit/', views.edit_contract, name='edit'),
    path('<int:pk>/delete/', views.delete_contract, name='delete'),
    path('<int:pk>/sign/', views.sign_contract, name='sign'),
    path('<int:pk>/download/', views.download_contract, name='download'),
    path('templates/', views.manage_templates, name='manage_templates'),
    path('templates/<int:template_id>/delete/', views.delete_template, name='delete_template'),
] 