from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('users/', include('users.urls', namespace='users')),
    path('campaigns/', include('campaigns.urls', namespace='campaigns')),
    path('contracts/', include('contracts.urls', namespace='contracts')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('content/', include('content.urls', namespace='content')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('discover/', include('discovery.urls', namespace='discovery')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'