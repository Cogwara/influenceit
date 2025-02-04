from django import forms
from .models import PerformanceMetric


class PerformanceMetricForm(forms.ModelForm):
    class Meta:
        model = PerformanceMetric
        fields = ('campaign', 'influencer', 'engagement_rate', 'reach', 'impressions',
                  'ctr', 'conversions', 'roi')
