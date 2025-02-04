from django.urls import path
from . import views

app_name = 'discovery'

urlpatterns = [
    # Main discovery pages
    path('', views.discovery_home, name='home'),
    path('influencers/', views.influencer_list, name='influencer_list'),
    path('brands/', views.brand_list, name='brand_list'),
    path('campaigns/', views.campaign_list, name='campaign_list'),

    # Detail pages
    path('influencers/<str:username>/',
         views.influencer_detail, name='influencer_detail'),
    path('brands/<str:username>/', views.brand_detail, name='brand_detail'),
    path('campaigns/<int:pk>/', views.campaign_detail, name='campaign_detail'),

    # Search and filter
    path('search/', views.search_results, name='search'),
    path('filter/', views.filter_results, name='filter'),

    # Categories and niches
    path('categories/', views.category_list, name='category_list'),
    path('categories/<str:slug>/', views.category_detail, name='category_detail'),
    path('niches/', views.niche_list, name='niche_list'),
    path('niches/<str:slug>/', views.niche_detail, name='niche_detail'),

    # Advanced features
    path('trending/', views.trending_content, name='trending'),
    path('recommended/', views.recommended_content, name='recommended'),
    path('saved/', views.saved_items, name='saved_items'),

    # API endpoints for dynamic loading
    path('api/load-more/', views.load_more, name='load_more'),
    path('api/quick-view/<int:pk>/', views.quick_view, name='quick_view'),

    # Actions
    path('save/<str:type>/<int:pk>/', views.save_item, name='save_item'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),

    # New influencer detail view
    path('influencer/<int:influencer_id>/', views.influencer_detail, name='influencer_detail'),

    # New brand detail view
    path('brand/<int:brand_id>/', views.brand_detail, name='brand_detail'),

    # New campaign detail view
    path('campaign/<int:pk>/', views.campaign_detail, name='campaign_detail'),
]
