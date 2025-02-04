from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.utils import timezone
from .models import Contract, ContractTemplate
from .forms import ContractTemplateForm, ContractForm
from campaigns.models import Campaign
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

class ContractListView(LoginRequiredMixin, ListView):
    model = Contract
    template_name = 'contracts/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.user_type == 'seeker':
            return Contract.objects.filter(campaign__creator=self.request.user)
        else:  # influencer
            return Contract.objects.filter(influencer=self.request.user)

class ContractDetailView(LoginRequiredMixin, DetailView):
    model = Contract
    template_name = 'contracts/contract_detail.html'
    context_object_name = 'contract'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_sign'] = self.object.can_sign(self.request.user)
        return context

@login_required
def contract_list(request):
    """View for listing contracts."""
    if request.user.is_brand:
        contracts = Contract.objects.filter(brand=request.user)
    else:
        contracts = Contract.objects.filter(influencer=request.user)
    
    return render(request, 'contracts/contract_list.html', {
        'contracts': contracts
    })

@login_required
def contract_detail(request, pk):
    """View for contract details."""
    contract = get_object_or_404(Contract, pk=pk)
    
    # Check permissions
    if request.user not in [contract.brand, contract.influencer]:
        raise PermissionDenied
    
    return render(request, 'contracts/contract_detail.html', {
        'contract': contract
    })

@login_required
def create_contract(request):
    """View for creating a new contract."""
    if not request.user.is_brand:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.brand = request.user
            contract.influencer = contract.campaign.creator
            contract.save()
            
            messages.success(request, 'Contract created successfully!')
            return redirect('contracts:detail', pk=contract.pk)
    else:
        form = ContractForm()
    
    return render(request, 'contracts/contract_form.html', {
        'form': form,
        'title': 'Create Contract'
    })

@login_required
def edit_contract(request, pk):
    """View for editing an existing contract."""
    contract = get_object_or_404(Contract, pk=pk)
    
    # Check permissions
    if request.user != contract.brand:
        raise PermissionDenied
    
    # Don't allow editing of signed contracts
    if contract.signed_by_brand or contract.signed_by_influencer:
        messages.error(request, 'Cannot edit a contract that has been signed.')
        return redirect('contracts:detail', pk=contract.pk)
    
    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contract updated successfully!')
            return redirect('contracts:detail', pk=contract.pk)
    else:
        form = ContractForm(instance=contract)
    
    return render(request, 'contracts/contract_form.html', {
        'form': form,
        'contract': contract,
        'title': 'Edit Contract'
    })

@login_required
def delete_contract(request, pk):
    """View for deleting a contract."""
    contract = get_object_or_404(Contract, pk=pk)
    
    # Check permissions
    if request.user != contract.brand:
        raise PermissionDenied
    
    # Don't allow deletion of signed contracts
    if contract.signed_by_brand or contract.signed_by_influencer:
        messages.error(request, 'Cannot delete a contract that has been signed.')
        return redirect('contracts:detail', pk=contract.pk)
    
    if request.method == 'POST':
        contract.delete()
        messages.success(request, 'Contract deleted successfully!')
        return redirect('contracts:list')
    
    return render(request, 'contracts/contract_confirm_delete.html', {
        'contract': contract
    })

@login_required
def sign_contract(request, pk):
    """View for signing a contract."""
    contract = get_object_or_404(Contract, pk=pk)
    
    # Check permissions
    if request.user not in [contract.brand, contract.influencer]:
        raise PermissionDenied
    
    if request.method == 'POST':
        if request.user == contract.brand:
            if not contract.signed_by_brand:
                contract.signed_by_brand = timezone.now()
                contract.save()
                messages.success(request, 'Contract signed successfully!')
            else:
                messages.warning(request, 'You have already signed this contract.')
        else:  # Influencer
            if not contract.signed_by_influencer:
                contract.signed_by_influencer = timezone.now()
                contract.save()
                messages.success(request, 'Contract signed successfully!')
            else:
                messages.warning(request, 'You have already signed this contract.')
        
        # If both parties have signed, update status
        if contract.signed_by_brand and contract.signed_by_influencer:
            contract.status = 'active'
            contract.save()
        
        return redirect('contracts:detail', pk=contract.pk)
    
    return render(request, 'contracts/contract_sign.html', {
        'contract': contract
    })

@login_required
def manage_templates(request):
    templates = ContractTemplate.objects.filter(creator=request.user)
    if request.method == 'POST':
        form = ContractTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.creator = request.user
            template.save()
            messages.success(request, 'Template created successfully!')
            return redirect('contracts:manage_templates')
    else:
        form = ContractTemplateForm()
    
    return render(request, 'contracts/manage_templates.html', {
        'templates': templates,
        'form': form
    })

@login_required
def delete_template(request, template_id):
    template = get_object_or_404(ContractTemplate, id=template_id, creator=request.user)
    template.delete()
    messages.success(request, 'Template deleted successfully!')
    return redirect('contracts:manage_templates')

@login_required
def download_contract(request, pk):
    """View for downloading contract as PDF."""
    contract = get_object_or_404(Contract, pk=pk)
    
    # Check permissions
    if request.user not in [contract.brand, contract.influencer]:
        raise PermissionDenied
    
    # Generate PDF logic here
    # You'll need to implement PDF generation using a library like ReportLab or WeasyPrint
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contract_{contract.contract_number}.pdf"'
    
    # Add PDF generation code here
    
    return response
