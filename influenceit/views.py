from django.shortcuts import render
from campaigns.models import Campaign


def index(request):
    campaigns = Campaign.objects.all()
    return render(request, 'index.html', {'campaigns': campaigns})