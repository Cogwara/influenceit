from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib import messages
from .models import InfluencerList, SearchFilter
from .forms import SearchFilterForm, InfluencerListForm
from users.models import InfluencerProfile

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
                queryset = queryset.filter(platforms__in=filters.getlist('platform'))
            if 'followers_min' in filters:
                queryset = queryset.filter(metrics__followers__gte=filters['followers_min'])
            if 'engagement_rate_min' in filters:
                queryset = queryset.filter(metrics__engagement_rate__gte=filters['engagement_rate_min'])

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
            influencer_list = InfluencerList.objects.get(id=list_id, creator=request.user)
            influencer_list.influencers.add(influencer_id)
            messages.success(request, 'Influencer added to list successfully!')
        except InfluencerList.DoesNotExist:
            messages.error(request, 'List not found!')
    return redirect('discovery:search')
