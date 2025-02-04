from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .models import Campaign, CampaignApplication, CampaignCategory
from .forms import CampaignForm, CampaignApplicationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator

class CampaignListView(ListView):
    model = Campaign
    template_name = 'campaigns/campaign_list.html'
    context_object_name = 'campaigns'
    paginate_by = 10

    def get_queryset(self):
        queryset = Campaign.objects.filter(status='active')
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(categories__slug=category)
        return queryset.order_by('-created_at')

class CampaignDetailView(DetailView):
    model = Campaign
    template_name = 'campaigns/campaign_detail.html'
    context_object_name = 'campaign'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_application'] = CampaignApplication.objects.filter(
                campaign=self.object,
                influencer=self.request.user
            ).first()
        return context

class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaigns/campaign_form.html'
    success_url = reverse_lazy('campaigns:list')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.success(self.request, 'Campaign created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Campaign'
        return context

class CampaignUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaigns/campaign_form.html'

    def test_func(self):
        campaign = self.get_object()
        return self.request.user == campaign.creator

    def get_success_url(self):
        return reverse_lazy('campaigns:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Campaign updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Campaign'
        return context

class CampaignDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Campaign
    template_name = 'campaigns/campaign_confirm_delete.html'
    success_url = reverse_lazy('campaigns:list')

    def test_func(self):
        campaign = self.get_object()
        return self.request.user == campaign.creator

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Campaign deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def apply_to_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if CampaignApplication.objects.filter(campaign=campaign, influencer=request.user).exists():
        messages.error(request, 'You have already applied to this campaign.')
        return redirect('campaigns:detail', pk=pk)
    
    if request.method == 'POST':
        form = CampaignApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.campaign = campaign
            application.influencer = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('campaigns:detail', pk=pk)
    else:
        form = CampaignApplicationForm()
    
    return render(request, 'campaigns/campaign_apply.html', {
        'form': form,
        'campaign': campaign
    })

@require_POST
@login_required
def update_application_status(request, pk):
    """Update the status of a campaign application."""
    application = get_object_or_404(CampaignApplication, pk=pk)
    
    # Check if user has permission to update status
    if application.campaign.creator != request.user:
        raise PermissionDenied
    
    new_status = request.POST.get('status')
    if new_status in dict(CampaignApplication.STATUS_CHOICES):
        application.status = new_status
        application.save()
        
        # Send notification to influencer (you can implement this later)
        # notify_status_change(application)
        
        if request.is_ajax():
            return JsonResponse({
                'status': 'success',
                'message': 'Application status updated successfully!',
                'new_status': application.get_status_display()
            })
        
        messages.success(request, 'Application status updated successfully!')
    else:
        if request.is_ajax():
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid status provided.'
            }, status=400)
        
        messages.error(request, 'Invalid status provided.')
    
    return redirect('campaigns:manage_applications', pk=application.campaign.pk)

@login_required
def manage_applications(request, pk):
    """View to manage applications for a campaign."""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    # Check if user has permission to manage applications
    if campaign.creator != request.user:
        raise PermissionDenied
    
    applications = campaign.applications.all().select_related('influencer').order_by('-created_at')
    
    return render(request, 'campaigns/manage_applications.html', {
        'campaign': campaign,
        'applications': applications,
        'status_choices': CampaignApplication.STATUS_CHOICES
    })

def search_campaigns(request):
    """Search campaigns based on various criteria."""
    query = request.GET.get('q', '')
    category = request.GET.get('category')
    budget_min = request.GET.get('budget_min')
    budget_max = request.GET.get('budget_max')
    status = request.GET.get('status')

    # Start with all active campaigns
    campaigns = Campaign.objects.filter(status='active')

    # Apply search filters
    if query:
        campaigns = campaigns.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(requirements__icontains=query) |
            Q(creator__username__icontains=query)
        )

    # Apply category filter
    if category:
        campaigns = campaigns.filter(categories__slug=category)

    # Apply budget range filter
    if budget_min:
        campaigns = campaigns.filter(budget__gte=float(budget_min))
    if budget_max:
        campaigns = campaigns.filter(budget__lte=float(budget_max))

    # Apply status filter
    if status:
        campaigns = campaigns.filter(status=status)

    # Order by most recent
    campaigns = campaigns.order_by('-created_at')

    # Pagination
    paginator = Paginator(campaigns, 12)  # Show 12 campaigns per page
    page = request.GET.get('page')
    campaigns = paginator.get_page(page)

    # Get all categories for filter dropdown
    categories = CampaignCategory.objects.all()

    context = {
        'campaigns': campaigns,
        'query': query,
        'selected_category': category,
        'budget_min': budget_min,
        'budget_max': budget_max,
        'selected_status': status,
        'categories': categories,
        'status_choices': Campaign.STATUS_CHOICES,
    }

    return render(request, 'campaigns/search_results.html', context)

class CategoryCampaignListView(ListView):
    model = Campaign
    template_name = 'campaigns/category_campaigns.html'
    context_object_name = 'campaigns'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(CampaignCategory, slug=self.kwargs['category'])
        queryset = Campaign.objects.filter(
            categories=self.category,
            status='active'
        )

        # Apply budget filters
        min_budget = self.request.GET.get('min_budget')
        max_budget = self.request.GET.get('max_budget')
        if min_budget:
            queryset = queryset.filter(budget__gte=float(min_budget))
        if max_budget:
            queryset = queryset.filter(budget__lte=float(max_budget))

        # Apply sorting
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'budget_high':
            queryset = queryset.order_by('-budget')
        elif sort == 'budget_low':
            queryset = queryset.order_by('budget')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'category': self.category,
            'categories': CampaignCategory.objects.all(),
            'current_sort': self.request.GET.get('sort', 'newest')
        })
        return context
