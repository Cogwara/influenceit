from django import forms
from .models import PaymentMethod

class PaymentMethodForm(forms.ModelForm):
    card_number = forms.CharField(max_length=16, min_length=16)
    exp_month = forms.IntegerField(min_value=1, max_value=12)
    exp_year = forms.IntegerField(min_value=2024)  # Adjust min_value based on current year
    cvc = forms.CharField(max_length=4, min_length=3)

    class Meta:
        model = PaymentMethod
        fields = []  # We don't actually save these fields directly

    def clean_card_number(self):
        number = self.cleaned_data['card_number']
        if not number.isdigit():
            raise forms.ValidationError("Card number must contain only digits.")
        return number

    def clean_cvc(self):
        cvc = self.cleaned_data['cvc']
        if not cvc.isdigit():
            raise forms.ValidationError("CVC must contain only digits.")
        return cvc

class PaymentFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'All'),
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed')
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    min_amount = forms.DecimalField(required=False)
    max_amount = forms.DecimalField(required=False) 