from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Avg, Count, F
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek
from django.utils import timezone
from datetime import timedelta
from campaigns.models import Campaign
from content.models import Content
from payments.models import Payment
from contracts.models import Contract
from django.http import HttpResponse, JsonResponse
import csv

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Date ranges
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        if user.user_type == 'seeker':
            # Campaign metrics
            campaigns = Campaign.objects.filter(creator=user)
            context['total_campaigns'] = campaigns.count()
            context['active_campaigns'] = campaigns.filter(status='active').count()
            
            # Content metrics
            content = Content.objects.filter(campaign__creator=user)
            context['total_content'] = content.count()
            context['content_by_platform'] = (
                content.values('type')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            # Financial metrics
            payments = Payment.objects.filter(payer=user)
            context['total_spent'] = payments.aggregate(total=Sum('amount'))['total'] or 0
            context['avg_campaign_cost'] = context['total_spent'] / context['total_campaigns'] if context['total_campaigns'] > 0 else 0
            
            # Performance metrics
            context['avg_engagement_rate'] = content.aggregate(
                avg=Avg('metrics__engagement_rate')
            )['avg'] or 0
            
        else:  # influencer
            # Campaign metrics
            campaigns = Campaign.objects.filter(contracts__influencer=user)
            context['total_campaigns'] = campaigns.count()
            context['active_campaigns'] = campaigns.filter(status='active').count()
            
            # Content metrics
            content = Content.objects.filter(creator=user)
            context['total_content'] = content.count()
            context['content_by_platform'] = (
                content.values('type')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            # Financial metrics
            payments = Payment.objects.filter(recipient=user)
            context['total_earned'] = payments.aggregate(total=Sum('amount'))['total'] or 0
            context['avg_campaign_earnings'] = context['total_earned'] / context['total_campaigns'] if context['total_campaigns'] > 0 else 0
            
            # Performance metrics
            context['avg_engagement_rate'] = content.aggregate(
                avg=Avg('metrics__engagement_rate')
            )['avg'] or 0
        
        # Time series data
        context['daily_metrics'] = self.get_daily_metrics(user, start_date, end_date)
        
        return context

    def get_daily_metrics(self, user, start_date, end_date):
        if user.user_type == 'seeker':
            content = Content.objects.filter(campaign__creator=user)
            payments = Payment.objects.filter(payer=user)
        else:
            content = Content.objects.filter(creator=user)
            payments = Payment.objects.filter(recipient=user)
        
        # Get daily content metrics
        daily_content = (
            content.filter(created_at__range=[start_date, end_date])
            .annotate(date=TruncDay('created_at'))
            .values('date')
            .annotate(
                content_count=Count('id'),
                avg_engagement=Avg('metrics__engagement_rate'),
                total_impressions=Sum('metrics__impressions')
            )
            .order_by('date')
        )
        
        # Get daily financial metrics
        daily_payments = (
            payments.filter(created_at__range=[start_date, end_date])
            .annotate(date=TruncDay('created_at'))
            .values('date')
            .annotate(total_amount=Sum('amount'))
            .order_by('date')
        )
        
        return {
            'content': list(daily_content),
            'payments': list(daily_payments)
        }

@login_required
def campaign_analytics(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    
    if request.user not in [campaign.creator, campaign.influencer]:
        messages.error(request, 'You are not authorized to view these analytics.')
        return redirect('campaigns:detail', pk=campaign_id)
    
    # Get campaign content
    content = Content.objects.filter(campaign=campaign)
    
    # Calculate metrics
    total_impressions = sum(c.metrics.get('impressions', 0) for c in content)
    total_engagement = sum(c.metrics.get('engagement_count', 0) for c in content)
    avg_engagement_rate = (
        total_engagement / total_impressions * 100 if total_impressions > 0 else 0
    )
    
    # Get content performance by platform
    platform_metrics = (
        content.values('type')
        .annotate(
            count=Count('id'),
            impressions=Sum('metrics__impressions'),
            engagement=Avg('metrics__engagement_rate')
        )
        .order_by('-count')
    )
    
    # Get timeline data
    timeline_data = (
        content.annotate(date=TruncDay('created_at'))
        .values('date')
        .annotate(
            content_count=Count('id'),
            impressions=Sum('metrics__impressions'),
            engagement=Avg('metrics__engagement_rate')
        )
        .order_by('date')
    )
    
    return render(request, 'analytics/campaign_analytics.html', {
        'campaign': campaign,
        'total_content': content.count(),
        'total_impressions': total_impressions,
        'total_engagement': total_engagement,
        'avg_engagement_rate': avg_engagement_rate,
        'platform_metrics': platform_metrics,
        'timeline_data': timeline_data
    })

@login_required
def export_analytics(request):
    user = request.user
    
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if user.user_type == 'seeker':
        data = generate_brand_analytics_report(user, start_date, end_date)
    else:
        data = generate_influencer_analytics_report(user, start_date, end_date)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analytics_{timezone.now()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Metric', 'Value'])
    
    for key, value in data.items():
        writer.writerow([key, value])
    
    return response

@login_required
def content_analytics(request):
    """View for displaying content analytics dashboard."""
    
    # Get time period from request (default to last 30 days)
    period = request.GET.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    start_date = timezone.now() - timedelta(days=days)
    
    # Get user's content based on role
    if request.user.is_brand:
        content_queryset = Content.objects.filter(
            contract__brand=request.user,
            created_at__gte=start_date
        )
    else:
        content_queryset = Content.objects.filter(
            creator=request.user,
            created_at__gte=start_date
        )

    # Calculate analytics
    analytics = {
        'total_content': content_queryset.count(),
        'total_views': content_queryset.aggregate(Sum('views'))['views__sum'] or 0,
        'total_likes': content_queryset.aggregate(Sum('likes'))['likes__sum'] or 0,
        'total_shares': content_queryset.aggregate(Sum('shares'))['shares__sum'] or 0,
        'total_comments': content_queryset.aggregate(Sum('comments'))['comments__sum'] or 0,
        'avg_engagement_rate': content_queryset.filter(views__gt=0).aggregate(
            avg_rate=Avg('likes') + Avg('shares') + Avg('comments')
        )['avg_rate'] or 0,
    }

    # Content performance by platform
    platform_stats = content_queryset.values('platform').annotate(
        count=Count('id'),
        total_views=Sum('views'),
        total_likes=Sum('likes'),
        total_shares=Sum('shares'),
        total_comments=Sum('comments')
    )

    # Content performance by type
    type_stats = content_queryset.values('content_type').annotate(
        count=Count('id'),
        total_views=Sum('views'),
        total_likes=Sum('likes'),
        total_shares=Sum('shares'),
        total_comments=Sum('comments')
    )

    # Top performing content
    top_content = content_queryset.order_by('-views', '-likes')[:5]

    # Recent content
    recent_content = content_queryset.order_by('-created_at')[:5]

    context = {
        'analytics': analytics,
        'platform_stats': platform_stats,
        'type_stats': type_stats,
        'top_content': top_content,
        'recent_content': recent_content,
        'selected_period': period,
        'start_date': start_date.date(),
        'end_date': timezone.now().date(),
    }

    return render(request, 'analytics/content_analytics.html', context)

@login_required
def performance_analytics(request):
    """View for displaying performance analytics dashboard."""
    
    # Get time period from request (default to last 30 days)
    period = request.GET.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    start_date = timezone.now() - timedelta(days=days)
    
    # Get user's data based on role
    if request.user.is_brand:
        campaigns = Campaign.objects.filter(creator=request.user)
        contracts = Contract.objects.filter(brand=request.user)
        content = Content.objects.filter(contract__brand=request.user)
    else:
        campaigns = Campaign.objects.filter(applications__influencer=request.user)
        contracts = Contract.objects.filter(influencer=request.user)
        content = Content.objects.filter(creator=request.user)

    # Filter by date range
    campaigns = campaigns.filter(created_at__gte=start_date)
    contracts = contracts.filter(created_at__gte=start_date)
    content = content.filter(created_at__gte=start_date)

    # Calculate key metrics
    performance_metrics = {
        'total_campaigns': campaigns.count(),
        'total_contracts': contracts.count(),
        'total_content': content.count(),
        'total_reach': content.aggregate(Sum('views'))['views__sum'] or 0,
        'total_engagement': (
            content.aggregate(
                total=Sum(F('likes') + F('shares') + F('comments'))
            )['total'] or 0
        ),
        'avg_engagement_rate': content.filter(views__gt=0).aggregate(
            rate=Avg((F('likes') + F('shares') + F('comments')) * 100.0 / F('views'))
        )['rate'] or 0,
    }

    # Monthly trends
    monthly_trends = content.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        content_count=Count('id'),
        total_views=Sum('views'),
        total_engagement=Sum(F('likes') + F('shares') + F('comments'))
    ).order_by('month')

    # Weekly performance
    weekly_performance = content.annotate(
        week=TruncWeek('created_at')
    ).values('week').annotate(
        content_count=Count('id'),
        total_views=Sum('views'),
        total_engagement=Sum(F('likes') + F('shares') + F('comments'))
    ).order_by('week')

    # Platform performance
    platform_performance = content.values('platform').annotate(
        content_count=Count('id'),
        total_views=Sum('views'),
        total_engagement=Sum(F('likes') + F('shares') + F('comments')),
        avg_engagement_rate=Avg((F('likes') + F('shares') + F('comments')) * 100.0 / F('views'))
    ).order_by('-total_views')

    # Campaign performance
    campaign_performance = campaigns.annotate(
        content_count=Count('contracts__content'),
        total_views=Sum('contracts__content__views'),
        total_engagement=Sum(
            F('contracts__content__likes') + 
            F('contracts__content__shares') + 
            F('contracts__content__comments')
        )
    ).order_by('-total_views')

    context = {
        'metrics': performance_metrics,
        'monthly_trends': monthly_trends,
        'weekly_performance': weekly_performance,
        'platform_performance': platform_performance,
        'campaign_performance': campaign_performance,
        'selected_period': period,
        'start_date': start_date.date(),
        'end_date': timezone.now().date(),
    }

    return render(request, 'analytics/performance_analytics.html', context)

@login_required
def get_metrics(request, metric_type):
    """View for getting specific metrics data."""
    
    # Get time period from request (default to last 30 days)
    period = request.GET.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    start_date = timezone.now() - timedelta(days=days)
    
    # Initialize response data
    data = {
        'labels': [],
        'datasets': [],
        'summary': {}
    }
    
    # Get user's base queryset based on role
    if request.user.is_brand:
        content_qs = Content.objects.filter(contract__brand=request.user)
        contracts_qs = Contract.objects.filter(brand=request.user)
        campaigns_qs = Campaign.objects.filter(creator=request.user)
    else:
        content_qs = Content.objects.filter(creator=request.user)
        contracts_qs = Contract.objects.filter(influencer=request.user)
        campaigns_qs = Campaign.objects.filter(applications__influencer=request.user)

    # Filter by date range
    content_qs = content_qs.filter(created_at__gte=start_date)
    contracts_qs = contracts_qs.filter(created_at__gte=start_date)
    campaigns_qs = campaigns_qs.filter(created_at__gte=start_date)

    if metric_type == 'engagement':
        # Engagement metrics
        engagement_data = content_qs.aggregate(
            total_likes=Sum('likes'),
            total_comments=Sum('comments'),
            total_shares=Sum('shares'),
            total_views=Sum('views')
        )
        
        data['summary'] = {
            'total_engagement': (
                (engagement_data['total_likes'] or 0) +
                (engagement_data['total_comments'] or 0) +
                (engagement_data['total_shares'] or 0)
            ),
            'engagement_rate': calculate_engagement_rate(engagement_data),
            'total_views': engagement_data['total_views'] or 0
        }
        
        # Engagement by platform
        platform_data = content_qs.values('platform').annotate(
            total_engagement=Sum(F('likes') + F('comments') + F('shares')),
            avg_engagement_rate=Avg((F('likes') + F('comments') + F('shares')) * 100.0 / F('views'))
        ).order_by('-total_engagement')
        
        data['datasets'] = [{
            'label': 'Engagement by Platform',
            'data': [item['total_engagement'] for item in platform_data],
            'backgroundColor': get_chart_colors(len(platform_data))
        }]
        data['labels'] = [item['platform'] for item in platform_data]

    elif metric_type == 'revenue':
        # Revenue metrics
        revenue_data = contracts_qs.aggregate(
            total_value=Sum('contract_value'),
            avg_value=Avg('contract_value'),
            contract_count=Count('id')
        )
        
        data['summary'] = {
            'total_revenue': float(revenue_data['total_value'] or 0),
            'average_contract_value': float(revenue_data['avg_value'] or 0),
            'total_contracts': revenue_data['contract_count'] or 0
        }
        
        # Monthly revenue
        monthly_revenue = contracts_qs.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            revenue=Sum('contract_value')
        ).order_by('month')
        
        data['datasets'] = [{
            'label': 'Monthly Revenue',
            'data': [float(item['revenue'] or 0) for item in monthly_revenue],
            'borderColor': '#36A2EB',
            'fill': False
        }]
        data['labels'] = [item['month'].strftime('%B %Y') for item in monthly_revenue]

    elif metric_type == 'performance':
        # Performance metrics
        performance_data = campaigns_qs.annotate(
            content_count=Count('contracts__content'),
            total_views=Sum('contracts__content__views'),
            total_engagement=Sum(
                F('contracts__content__likes') +
                F('contracts__content__comments') +
                F('contracts__content__shares')
            )
        ).aggregate(
            total_campaigns=Count('id'),
            total_content=Sum('content_count'),
            total_views=Sum('total_views'),
            total_engagement=Sum('total_engagement')
        )
        
        data['summary'] = {
            'total_campaigns': performance_data['total_campaigns'] or 0,
            'total_content': performance_data['total_content'] or 0,
            'total_views': performance_data['total_views'] or 0,
            'total_engagement': performance_data['total_engagement'] or 0
        }
        
        # Performance by campaign
        campaign_performance = campaigns_qs.annotate(
            content_count=Count('contracts__content'),
            total_views=Sum('contracts__content__views'),
            total_engagement=Sum(
                F('contracts__content__likes') +
                F('contracts__content__comments') +
                F('contracts__content__shares')
            )
        ).values('title', 'total_views', 'total_engagement')
        
        data['datasets'] = [
            {
                'label': 'Views',
                'data': [item['total_views'] or 0 for item in campaign_performance],
                'backgroundColor': '#36A2EB'
            },
            {
                'label': 'Engagement',
                'data': [item['total_engagement'] or 0 for item in campaign_performance],
                'backgroundColor': '#FF6384'
            }
        ]
        data['labels'] = [item['title'] for item in campaign_performance]

    else:
        return JsonResponse({'error': 'Invalid metric type'}, status=400)

    return JsonResponse(data)

def calculate_engagement_rate(data):
    """Calculate engagement rate from aggregated data."""
    total_engagement = (
        (data['total_likes'] or 0) +
        (data['total_comments'] or 0) +
        (data['total_shares'] or 0)
    )
    total_views = data['total_views'] or 0
    
    if total_views > 0:
        return (total_engagement / total_views) * 100
    return 0

def get_chart_colors(count):
    """Generate chart colors."""
    colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#7BC225', '#B56DED'
    ]
    return colors[:count]
