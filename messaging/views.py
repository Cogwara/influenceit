from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.db.models import Q, Max, Prefetch
from django.utils import timezone
from .models import Conversation, Message
from .forms import MessageForm
from users.models import CustomUser

class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'messaging/inbox.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        return (Conversation.objects
                .filter(participants=self.request.user)
                .annotate(last_message_time=Max('messages__timestamp'))
                .order_by('-last_message_time'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_form'] = MessageForm()
        return context

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related('messages', 'participants'),
        id=conversation_id,
        participants=request.user
    )
    
    # Mark messages as read
    Message.objects.filter(
        conversation=conversation,
        read_by__exclude=request.user
    ).update(read_by=request.user)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': {
                        'content': message.content,
                        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M'),
                        'sender_name': message.sender.get_full_name(),
                        'sender_avatar': message.sender.profile_picture.url
                    }
                })
            return redirect('messaging:conversation_detail', conversation_id=conversation_id)
    else:
        form = MessageForm()

    context = {
        'conversation': conversation,
        'form': form
    }
    return render(request, 'messaging/conversation_detail.html', context)

@login_required
def create_conversation(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        recipient = get_object_or_404(CustomUser, id=recipient_id)
        
        # Check if conversation already exists
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=recipient
        ).first()
        
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, recipient)
        
        return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    
    # Get potential recipients based on user type
    if request.user.user_type == 'seeker':
        recipients = CustomUser.objects.filter(user_type='influencer')
    else:
        recipients = CustomUser.objects.filter(user_type='seeker')
    
    return render(request, 'messaging/create_conversation.html', {
        'recipients': recipients
    })

@login_required
def get_unread_count(request):
    count = Message.objects.filter(
        conversation__participants=request.user
    ).exclude(
        read_by=request.user
    ).count()
    
    return JsonResponse({'unread_count': count})

@login_required
def search_conversations(request):
    query = request.GET.get('q', '')
    conversations = Conversation.objects.filter(
        participants=request.user
    ).filter(
        Q(participants__username__icontains=query) |
        Q(participants__first_name__icontains=query) |
        Q(participants__last_name__icontains=query)
    ).distinct()
    
    results = [{
        'id': conv.id,
        'name': conv.get_other_participant(request.user).get_full_name(),
        'avatar': conv.get_other_participant(request.user).profile_picture.url,
        'last_message': conv.messages.last().content if conv.messages.exists() else ''
    } for conv in conversations]
    
    return JsonResponse({'results': results})
