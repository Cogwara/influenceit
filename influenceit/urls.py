from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('campaigns/', include('campaigns.urls')),
    path('contracts/', include('contracts.urls')),
    path('payments/', include('payments.urls')),
    path('content/', include('content.urls')),
    path('analytics/', include('analytics.urls')),
    path('notifications/', include('notifications.urls')),
    path('discover/', include('discovery.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)