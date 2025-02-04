import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(amount, currency='usd', metadata=None):
    """Create a PaymentIntent in Stripe."""
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency=currency,
            metadata=metadata or {},
        )
        return intent
    except stripe.error.StripeError as e:
        # Handle any errors from Stripe
        raise e

def create_customer(user, payment_method_id=None):
    """Create or update a Stripe Customer."""
    try:
        if hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
            # Update existing customer
            customer = stripe.Customer.modify(
                user.stripe_customer_id,
                email=user.email,
                payment_method=payment_method_id
            )
        else:
            # Create new customer
            customer = stripe.Customer.create(
                email=user.email,
                payment_method=payment_method_id,
                metadata={
                    'user_id': user.id
                }
            )
        return customer
    except stripe.error.StripeError as e:
        raise e

def create_refund(payment_intent_id, amount=None):
    """Create a refund in Stripe."""
    try:
        refund_params = {'payment_intent': payment_intent_id}
        if amount:
            refund_params['amount'] = int(amount * 100)
        
        refund = stripe.Refund.create(**refund_params)
        return refund
    except stripe.error.StripeError as e:
        raise e 