import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Payment

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        handle_successful_payment(payment_intent)
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        handle_failed_payment(payment_intent)

    return HttpResponse(status=200)

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