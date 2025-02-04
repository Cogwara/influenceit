from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from .models import Content, ContentReview
from .forms import ContentForm, ContentReviewForm
from campaigns.models import Campaign
from contracts.models import Contract
from django.urls import reverse_lazy

class ContentListView(LoginRequiredMixin, ListView):
    model = Content
    template_name = 'content/content_list.html'
    context_object_name = 'contents'
    paginate_by = 10

    def get_queryset(self):
        """
        Filter content based on user role:
        - Brands see content from their contracts
        - Influencers see their own content
        """
        queryset = Content.objects.all()
        
        if self.request.user.is_brand:
            return queryset.filter(contract__brand=self.request.user)
        else:
            return queryset.filter(contract__influencer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Content List'
        return context

class ContentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Content
    template_name = 'content/content_detail.html'
    context_object_name = 'content'

    def test_func(self):
        content = self.get_object()
        return (self.request.user == content.contract.brand or 
                self.request.user == content.contract.influencer)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = ContentReviewForm()
        context['reviews'] = self.object.reviews.all().order_by('-created_at')
        return context

class ContentCreateView(LoginRequiredMixin, CreateView):
    model = Content
    form_class = ContentForm
    template_name = 'content/content_form.html'
    success_url = reverse_lazy('content:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.success(self.request, 'Content created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Content'
        # Get available contracts for the user
        if self.request.user.is_brand:
            context['contracts'] = Contract.objects.filter(brand=self.request.user)
        else:
            context['contracts'] = Contract.objects.filter(influencer=self.request.user)
        return context

class ContentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Content
    form_class = ContentForm
    template_name = 'content/content_form.html'
    success_url = reverse_lazy('content:list')

    def test_func(self):
        content = self.get_object()
        return self.request.user == content.creator

    def form_valid(self, form):
        messages.success(self.request, 'Content updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Content'
        return context

class ContentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Content
    template_name = 'content/content_confirm_delete.html'
    success_url = reverse_lazy('content:list')

    def test_func(self):
        content = self.get_object()
        return self.request.user == content.creator

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Content deleted successfully!')
        return super().delete(request, *args, **kwargs)

def approve_content(request, pk):
    content = get_object_or_404(Content, pk=pk)
    
    # Check if user has permission to approve
    if request.user != content.contract.brand:
        messages.error(request, 'You do not have permission to approve this content.')
        return redirect('content:detail', pk=pk)
    
    content.status = 'approved'
    content.save()
    messages.success(request, 'Content approved successfully!')
    return redirect('content:detail', pk=pk)

def reject_content(request, pk):
    content = get_object_or_404(Content, pk=pk)
    
    # Check if user has permission to reject
    if request.user != content.contract.brand:
        messages.error(request, 'You do not have permission to reject this content.')
        return redirect('content:detail', pk=pk)
    
    content.status = 'rejected'
    content.save()
    messages.success(request, 'Content rejected successfully!')
    return redirect('content:detail', pk=pk)

@login_required
def create_content(request, campaign_id):
    campaign = get_object_or_404(
        Campaign,
        id=campaign_id,
        contracts__influencer=request.user,
        contracts__status='active'
    )
    
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.creator = request.user
            content.campaign = campaign
            content.save()
            
            messages.success(request, 'Content submitted successfully!')
            return redirect('content:detail', pk=content.id)
    else:
        form = ContentForm()
    
    return render(request, 'content/create_content.html', {
        'form': form,
        'campaign': campaign
    })

@login_required
def update_content(request, pk):
    content = get_object_or_404(Content, pk=pk, creator=request.user)
    
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            content = form.save()
            messages.success(request, 'Content updated successfully!')
            return redirect('content:detail', pk=content.id)
    else:
        form = ContentForm(instance=content)
    
    return render(request, 'content/update_content.html', {
        'form': form,
        'content': content
    })

@login_required
def review_content(request, pk):
    content = get_object_or_404(Content, pk=pk)
    
    # Only allow brand to review content
    if request.user != content.campaign.creator:
        messages.error(request, 'You are not authorized to review this content.')
        return redirect('content:detail', pk=pk)
    
    if request.method == 'POST':
        form = ContentReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.content = content
            review.reviewer = request.user
            review.save()
            
            # Update content status based on review
            if review.status == 'approved':
                content.status = 'approved'
            elif review.status == 'rejected':
                content.status = 'rejected'
            content.save()
            
            messages.success(request, 'Review submitted successfully!')
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'review': {
                        'feedback': review.feedback,
                        'status': review.get_status_display(),
                        'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
                    }
                })
            return redirect('content:detail', pk=pk)
    
    return redirect('content:detail', pk=pk)

@login_required
def update_metrics(request, pk):
    content = get_object_or_404(Content, pk=pk, creator=request.user)
    
    if request.method == 'POST':
        metrics = request.POST.dict()
        metrics.pop('csrfmiddlewaretoken', None)
        
        content.metrics = metrics
        content.save()
        
        messages.success(request, 'Metrics updated successfully!')
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def content_analytics(request, pk):
    content = get_object_or_404(Content, pk=pk)
    
    if request.user not in [content.creator, content.campaign.creator]:
        messages.error(request, 'You are not authorized to view these analytics.')
        return redirect('content:detail', pk=pk)
    
    # Get historical metrics
    from analytics.models import ContentMetric
    metrics = ContentMetric.objects.filter(content=content).order_by('timestamp')
    
    analytics_data = {
        'labels': [m.timestamp.strftime('%Y-%m-%d') for m in metrics],
        'engagement': [m.metrics.get('engagement_rate', 0) for m in metrics],
        'impressions': [m.metrics.get('impressions', 0) for m in metrics],
        'likes': [m.metrics.get('likes', 0) for m in metrics],
        'comments': [m.metrics.get('comments', 0) for m in metrics]
    }
    
    return render(request, 'content/analytics.html', {
        'content': content,
        'analytics_data': analytics_data
    })
