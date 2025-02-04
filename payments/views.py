from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import Payment, PaymentMethod, Invoice
from .forms import PaymentMethodForm
from .utils import create_payment_intent, create_customer
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.user_type == 'seeker':
            return Payment.objects.filter(payer=self.request.user)
        else:  # influencer
            return Payment.objects.filter(recipient=self.request.user)

class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context

@login_required
def add_payment_method(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            try:
                # Create Stripe payment method
                payment_method = stripe.PaymentMethod.create(
                    type='card',
                    card={
                        'number': form.cleaned_data['card_number'],
                        'exp_month': form.cleaned_data['exp_month'],
                        'exp_year': form.cleaned_data['exp_year'],
                        'cvc': form.cleaned_data['cvc'],
                    },
                )

                # Attach payment method to customer
                if not request.user.stripe_customer_id:
                    customer = stripe.Customer.create(
                        email=request.user.email,
                        payment_method=payment_method.id,
                    )
                    request.user.stripe_customer_id = customer.id
                    request.user.save()
                else:
                    stripe.PaymentMethod.attach(
                        payment_method.id,
                        customer=request.user.stripe_customer_id,
                    )

                # Save payment method to database
                PaymentMethod.objects.create(
                    user=request.user,
                    stripe_payment_method_id=payment_method.id,
                    card_last4=form.cleaned_data['card_number'][-4:],
                    card_brand=payment_method.card.brand,
                    exp_month=form.cleaned_data['exp_month'],
                    exp_year=form.cleaned_data['exp_year'],
                )

                messages.success(request, 'Payment method added successfully!')
                return redirect('payments:payment_methods')

            except stripe.error.StripeError as e:
                messages.error(request, f'Error adding payment method: {str(e)}')
    else:
        form = PaymentMethodForm()

    return render(request, 'payments/add_payment_method.html', {'form': form})

@login_required
def payment_methods(request):
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    return render(request, 'payments/payment_methods.html', {
        'payment_methods': payment_methods
    })

@login_required
def remove_payment_method(request, method_id):
    payment_method = get_object_or_404(PaymentMethod, id=method_id, user=request.user)
    try:
        stripe.PaymentMethod.detach(payment_method.stripe_payment_method_id)
        payment_method.delete()
        messages.success(request, 'Payment method removed successfully!')
    except stripe.error.StripeError as e:
        messages.error(request, f'Error removing payment method: {str(e)}')
    return redirect('payments:payment_methods')

@login_required
def process_payment(request, campaign_id):
    from campaigns.models import Campaign
    campaign = get_object_or_404(Campaign, id=campaign_id, creator=request.user)

    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method_id')
        payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=request.user)

        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(campaign.budget * 100),  # Convert to cents
                currency='usd',
                customer=request.user.stripe_customer_id,
                payment_method=payment_method.stripe_payment_method_id,
                off_session=True,
                confirm=True,
            )

            # Create payment record
            payment = Payment.objects.create(
                campaign=campaign,
                payer=request.user,
                recipient=campaign.influencer,
                amount=campaign.budget,
                status='completed',
                stripe_payment_intent_id=intent.id
            )

            # Create invoice
            Invoice.objects.create(
                payment=payment,
                invoice_number=f'INV-{payment.id}',
                status='paid'
            )

            messages.success(request, 'Payment processed successfully!')
            return redirect('payments:payment_detail', pk=payment.id)

        except stripe.error.StripeError as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('campaigns:detail', pk=campaign_id)

    return redirect('campaigns:detail', pk=campaign_id)

@login_required
def generate_invoice(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    invoice = payment.invoice

    if not invoice:
        messages.error(request, 'No invoice found for this payment.')
        return redirect('payments:payment_detail', pk=payment_id)

    # Generate PDF invoice
    from .utils import generate_invoice_pdf
    pdf = generate_invoice_pdf(invoice)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    response.write(pdf)
    return response

@login_required
def payment_analytics(request):
    if request.user.user_type == 'seeker':
        payments = Payment.objects.filter(payer=request.user)
    else:
        payments = Payment.objects.filter(recipient=request.user)

    # Calculate analytics
    total_spent = payments.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    payment_count = payments.filter(status='completed').count()
    average_payment = total_spent / payment_count if payment_count > 0 else 0

    # Get monthly trends
    from django.db.models.functions import TruncMonth
    monthly_trends = (payments
                     .filter(status='completed')
                     .annotate(month=TruncMonth('created_at'))
                     .values('month')
                     .annotate(total=Sum('amount'))
                     .order_by('month'))

    return render(request, 'payments/analytics.html', {
        'total_spent': total_spent,
        'payment_count': payment_count,
        'average_payment': average_payment,
        'monthly_trends': monthly_trends
    })

@login_required
def payment_process(request):
    if request.method == 'POST':
        try:
            # Get the payment amount from your form or contract
            amount = float(request.POST.get('amount'))
            
            # Create PaymentIntent
            intent = create_payment_intent(
                amount=amount,
                metadata={
                    'user_id': request.user.id,
                }
            )
            
            # Create Payment record
            payment = Payment.objects.create(
                payer=request.user,
                amount=amount,
                transaction_id=intent.id,
                status='pending'
            )
            
            return JsonResponse({
                'client_secret': intent.client_secret
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'payments/payment_form.html', {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

@login_required
def payment_success(request):
    payment = Payment.objects.filter(
        payer=request.user,
        status='completed'
    ).order_by('-created_at').first()
    
    return render(request, 'payments/success.html', {
        'payment': payment
    })

@login_required
def payment_error(request):
    error_message = request.GET.get('error')
    return render(request, 'payments/error.html', {
        'error_message': error_message
    })

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        handle_successful_payment(payment_intent)
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        handle_failed_payment(payment_intent)

    return JsonResponse({'status': 'success'})

def handle_successful_payment(payment_intent):
    """Handle successful payment webhook."""
    payment = Payment.objects.filter(
        transaction_id=payment_intent.id
    ).first()
    
    if payment:
        payment.status = 'completed'
        payment.stripe_data = payment_intent
        payment.save()
        
        # Update related models (e.g., contract status)
        if payment.contract:
            payment.contract.status = 'active'
            payment.contract.save()

def handle_failed_payment(payment_intent):
    """Handle failed payment webhook."""
    payment = Payment.objects.filter(
        transaction_id=payment_intent.id
    ).first()
    
    if payment:
        payment.status = 'failed'
        payment.stripe_data = payment_intent
        payment.save()

@login_required
def payment_history(request):
    """View for displaying payment history."""
    payments = Payment.objects.filter(payer=request.user).order_by('-created_at')
    return render(request, 'payments/history.html', {
        'payments': payments
    })

@login_required
def payment_detail(request, pk):
    """View for displaying payment details."""
    payment = get_object_or_404(Payment, pk=pk, payer=request.user)
    return render(request, 'payments/detail.html', {
        'payment': payment
    })
