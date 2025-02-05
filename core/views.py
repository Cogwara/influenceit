from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from .models import FAQ, ContactMessage
from .forms import ContactForm, NewsletterForm
from campaigns.models import Campaign
from users.models import CustomUser


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_campaigns'] = Campaign.objects.filter(
            status='active',
            is_featured=True
        )[:6]
        context['top_influencers'] = CustomUser.objects.filter(
            user_type='influencer',
            is_verified=True
        ).order_by('-total_followers')[:4]
        context['newsletter_form'] = NewsletterForm()
        return context


class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_campaigns'] = Campaign.objects.count()
        context['total_influencers'] = CustomUser.objects.filter(
            user_type='influencer'
        ).count()
        context['total_brands'] = CustomUser.objects.filter(
            user_type='seeker'
        ).count()
        return context


class ContactView(TemplateView):
    template_name = 'core/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save()

            # Send email notification
            send_mail(
                subject=f'New Contact Message: {message.subject}',
                message=f'From: {message.name} ({message.email})\n\n{
                    message.message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
            )

            messages.success(
                request, 'Your message has been sent successfully!')
            return redirect('core:contact')

        return render(request, self.template_name, {'form': form})


class FAQView(ListView):
    model = FAQ
    template_name = 'core/faq.html'
    context_object_name = 'faqs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = FAQ.CATEGORY_CHOICES
        return context


class TermsView(TemplateView):
    template_name = 'core/terms.html'


class PrivacyView(TemplateView):
    template_name = 'core/privacy.html'


def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Add email to newsletter service (e.g., Mailchimp)
            messages.success(
                request, 'Thank you for subscribing to our newsletter!')
        else:
            messages.error(request, 'Please enter a valid email address.')
    return redirect('core:home')


def handler404(request, exception):
    """Custom 404 error handler."""
    return render(request, 'core/404.html', status=404)


def handler500(request):
    """Custom 500 error handler."""
    return render(request, 'core/500.html', status=500)


def about_view(request):
    return render(request, 'core/about.html')
