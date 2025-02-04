from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.utils import timezone
from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return (Notification.objects
                .filter(recipient=self.request.user)
                .order_by('-created_at'))

@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(
        Notification, 
        pk=pk, 
        recipient=request.user
    )
    notification.mark_as_read()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications:list')

@login_required
def mark_all_as_read(request):
    Notification.objects.filter(
        recipient=request.user,
        read_at__isnull=True
    ).update(read_at=timezone.now())
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications:list')

@login_required
def get_unread_count(request):
    count = Notification.objects.filter(
        recipient=request.user,
        read_at__isnull=True
    ).count()
    
    return JsonResponse({'count': count})

@login_required
def notification_preferences(request):
    if request.method == 'POST':
        preferences = request.POST.dict()
        preferences.pop('csrfmiddlewaretoken', None)
        
        user = request.user
        user.notification_preferences = preferences
        user.save()
        
        return JsonResponse({'status': 'success'})
    
    return render(request, 'notifications/preferences.html', {
        'preferences': request.user.notification_preferences
    })

@login_required
def get_recent_notifications(request):
    notifications = (Notification.objects
                    .filter(recipient=request.user)
                    .order_by('-created_at')[:5])
    
    data = [{
        'id': n.id,
        'message': n.message,
        'url': n.url,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
        'read': n.read_at is not None
    } for n in notifications]
    
    return JsonResponse({'notifications': data})
