from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.db.models import Q, Count
from users.models import InfluencerProfile, BrandProfile
from .models import InfluencerList, SearchFilter, Category, Niche, SavedItem
from .forms import SearchFilterForm, InfluencerListForm
from campaigns.models import Campaign


class InfluencerDiscoveryView(ListView):
    model = InfluencerProfile
    template_name = 'discovery/search.html'
    context_object_name = 'influencers'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = self.request.GET

        if filters:
            if 'niche' in filters:
                queryset = queryset.filter(niche__in=filters.getlist('niche'))
            if 'platform' in filters:
                queryset = queryset.filter(
                    platforms__in=filters.getlist('platform'))
            if 'followers_min' in filters:
                queryset = queryset.filter(
                    metrics__followers__gte=filters['followers_min'])
            if 'engagement_rate_min' in filters:
                queryset = queryset.filter(
                    metrics__engagement_rate__gte=filters['engagement_rate_min'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchFilterForm(self.request.GET or None)
        return context


@login_required
def save_search_filter(request):
    if request.method == 'POST':
        form = SearchFilterForm(request.POST)
        if form.is_valid():
            filter = form.save(commit=False)
            filter.user = request.user
            filter.save()
            messages.success(request, 'Search filter saved successfully!')
            return redirect('discovery:search')
    return redirect('discovery:search')


class InfluencerListView(ListView):
    model = InfluencerList
    template_name = 'discovery/lists.html'
    context_object_name = 'lists'

    def get_queryset(self):
        return InfluencerList.objects.filter(creator=self.user)


@login_required
def create_influencer_list(request):
    if request.method == 'POST':
        form = InfluencerListForm(request.POST)
        if form.is_valid():
            list = form.save(commit=False)
            list.creator = request.user
            list.save()
            form.save_m2m()
            messages.success(request, 'List created successfully!')
            return redirect('discovery:lists')
    else:
        form = InfluencerListForm()

    return render(request, 'discovery/create_list.html', {'form': form})


@login_required
def add_to_list(request, influencer_id):
    if request.method == 'POST':
        list_id = request.POST.get('list_id')
        try:
            influencer_list = InfluencerList.objects.get(
                id=list_id, creator=request.user)
            influencer_list.influencers.add(influencer_id)
            messages.success(request, 'Influencer added to list successfully!')
        except InfluencerList.DoesNotExist:
            messages.error(request, 'List not found!')
    return redirect('discovery:search')


def discovery_home(request):
    """Home page for discovery section"""
    trending_influencers = InfluencerProfile.objects.all()[:6]
    featured_campaigns = Campaign.objects.filter(status='active')[:3]
    categories = Category.objects.all()[:6]

    context = {
        'trending_influencers': trending_influencers,
        'featured_campaigns': featured_campaigns,
        'categories': categories,
    }
    return render(request, 'discovery/home.html', context)


def influencer_list(request):
    """List all influencers with filtering options"""
    influencers = InfluencerProfile.objects.all()
    form = SearchFilterForm(request.GET or None)

    if form.is_valid():
        # Apply filters from form
        pass

    context = {
        'influencers': influencers,
        'form': form,
    }
    return render(request, 'discovery/influencer_list.html', context)


def brand_list(request):
    """List all brands"""
    brands = BrandProfile.objects.all()
    context = {'brands': brands}
    return render(request, 'discovery/brand_list.html', context)


def campaign_list(request):
    """List all active campaigns"""
    campaigns = Campaign.objects.filter(status='active')
    context = {'campaigns': campaigns}
    return render(request, 'discovery/campaign_list.html', context)


def influencer_detail(request, username):
    """Show detailed influencer profile"""
    influencer = get_object_or_404(InfluencerProfile, user__username=username)
    context = {'influencer': influencer}
    return render(request, 'discovery/influencer_detail.html', context)


def brand_detail(request, username):
    """Show detailed brand profile"""
    brand = get_object_or_404(BrandProfile, user__username=username)
    context = {'brand': brand}
    return render(request, 'discovery/brand_detail.html', context)


def campaign_detail(request, pk):
    """Show campaign details"""
    campaign = get_object_or_404(Campaign, pk=pk)
    context = {'campaign': campaign}
    return render(request, 'discovery/campaign_detail.html', context)


def search_results(request):
    """Handle search functionality"""
    query = request.GET.get('q', '')
    results = []
    if query:
        results = InfluencerProfile.objects.filter(
            Q(user__username__icontains=query) |
            Q(bio__icontains=query)
        )
    context = {'results': results, 'query': query}
    return render(request, 'discovery/search_results.html', context)


def filter_results(request):
    """Handle advanced filtering"""
    form = SearchFilterForm(request.GET or None)
    results = InfluencerProfile.objects.all()
    if form.is_valid():
        # Apply filters
        pass
    context = {'form': form, 'results': results}
    return render(request, 'discovery/filter_results.html', context)


def category_list(request):
    """List all categories"""
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'discovery/category_list.html', context)


def category_detail(request, slug):
    """Show category details and related content"""
    category = get_object_or_404(Category, slug=slug)
    context = {'category': category}
    return render(request, 'discovery/category_detail.html', context)


def niche_list(request):
    """List all niches"""
    niches = Niche.objects.all()
    context = {'niches': niches}
    return render(request, 'discovery/niche_list.html', context)


def niche_detail(request, slug):
    """Show niche details and related content"""
    niche = get_object_or_404(Niche, slug=slug)
    context = {'niche': niche}
    return render(request, 'discovery/niche_detail.html', context)


def trending_content(request):
    """Show trending influencers and content"""
    trending_influencers = InfluencerProfile.objects.all()[:10]
    context = {'trending_influencers': trending_influencers}
    return render(request, 'discovery/trending.html', context)


@login_required
def recommended_content(request):
    """Show personalized recommendations"""
    recommended = InfluencerProfile.objects.all()[:10]
    context = {'recommended': recommended}
    return render(request, 'discovery/recommended.html', context)


@login_required
def saved_items(request):
    """Show user's saved items"""
    saved = request.user.saveditem_set.all()
    context = {'saved_items': saved}
    return render(request, 'discovery/saved_items.html', context)


def load_more(request):
    """API endpoint for infinite scrolling"""
    page = request.GET.get('page', 1)
    item_type = request.GET.get('type')
    # Return JSON response with more items
    return JsonResponse({'items': []})


def quick_view(request, pk):
    """API endpoint for quick view modal"""
    item = get_object_or_404(InfluencerProfile, pk=pk)
    data = {
        'name': item.user.get_full_name(),
        'bio': item.bio,
    }
    return JsonResponse(data)


@login_required
def save_item(request, type, pk):
    """Handle saving items to user's list"""
    if request.method == 'POST':
        # Handle saving
        pass
    return JsonResponse({'status': 'success'})


@login_required
def follow_user(request, username):
    """Handle following/unfollowing users"""
    if request.method == 'POST':
        # Handle following
        pass
    return JsonResponse({'status': 'success'})
