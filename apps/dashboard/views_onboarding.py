"""
Onboarding views for guiding new merchants through setup.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.accounts.utils import get_merchant
from apps.accounts.models_onboarding import OnboardingStep, OnboardingProgress


def check_onboarding_progress(merchant):
    """Automatically check and update onboarding progress based on merchant's actual state."""
    # Profile step: check if merchant has phone (logo is optional at registration)
    profile_step = merchant.onboarding_steps.filter(step_type='profile').first()
    if profile_step and not profile_step.completed:
        if merchant.phone:
            profile_step.mark_complete()
    
    # Program step: check if merchant has active program
    program_step = merchant.onboarding_steps.filter(step_type='program').first()
    if program_step and not program_step.completed:
        if merchant.programs.filter(active=True).exists():
            program_step.mark_complete()
    
    # Card step: check if merchant has any cards
    card_step = merchant.onboarding_steps.filter(step_type='card').first()
    if card_step and not card_step.completed:
        from apps.loyalty.models import LoyaltyCard
        if LoyaltyCard.objects.filter(program__merchant=merchant).exists():
            card_step.mark_complete()
    
    # Wallet step: check if Google Wallet is configured (has issuer ID)
    wallet_step = merchant.onboarding_steps.filter(step_type='wallet').first()
    if wallet_step and not wallet_step.completed:
        from django.conf import settings
        if getattr(settings, 'GOOGLE_WALLET_ISSUER_ID', None):
            wallet_step.mark_complete()
    
    # WhatsApp step: check if WhatsApp is connected
    whatsapp_step = merchant.onboarding_steps.filter(step_type='whatsapp').first()
    if whatsapp_step and not whatsapp_step.completed:
        if merchant.whatsapp_connected:
            whatsapp_step.mark_complete()
    
    # Update overall progress
    progress, _ = OnboardingProgress.objects.get_or_create(merchant=merchant)
    progress.update_progress()


@login_required
def onboarding_checklist(request):
    """Display onboarding checklist for the merchant."""
    merchant = get_merchant(request.user)
    if not merchant:
        return JsonResponse({'error': 'Commerce non trouvé'}, status=404)
    
    # Get or create onboarding progress
    progress, created = OnboardingProgress.objects.get_or_create(merchant=merchant)
    
    # Ensure all steps exist
    for step_type, _ in OnboardingStep.STEP_CHOICES:
        OnboardingStep.objects.get_or_create(
            merchant=merchant,
            step_type=step_type
        )
    
    # Auto-check progress
    check_onboarding_progress(merchant)
    
    # Get all steps
    steps = merchant.onboarding_steps.all()
    
    context = {
        'progress': progress,
        'steps': steps,
        'step_choices': OnboardingStep.STEP_CHOICES,
    }
    
    return render(request, 'dashboard/onboarding.html', context)


@login_required
def mark_step_complete(request, step_type):
    """Mark an onboarding step as complete."""
    merchant = get_merchant(request.user)
    if not merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    try:
        step = OnboardingStep.objects.get(
            merchant=merchant,
            step_type=step_type
        )
        step.mark_complete()
        
        # Update overall progress
        progress, _ = OnboardingProgress.objects.get_or_create(merchant=merchant)
        progress.update_progress()
        
        return JsonResponse({
            'success': True,
            'percentage': progress.percentage,
            'current_step': progress.current_step,
        })
    except OnboardingStep.DoesNotExist:
        return JsonResponse({'error': 'Étape non trouvée'}, status=404)


@login_required
def get_onboarding_status(request):
    """Get current onboarding status via AJAX."""
    merchant = get_merchant(request.user)
    if not merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    progress, created = OnboardingProgress.objects.get_or_create(merchant=merchant)
    
    if created:
        # Initialize all steps
        for step_type, _ in OnboardingStep.STEP_CHOICES:
            OnboardingStep.objects.get_or_create(
                merchant=merchant,
                step_type=step_type
            )
        progress.update_progress()
    
    # Auto-check progress
    check_onboarding_progress(merchant)
    
    steps = merchant.onboarding_steps.all()
    
    return JsonResponse({
        'percentage': progress.percentage,
        'current_step': progress.current_step,
        'completed': progress.percentage == 100,
        'steps': [
            {
                'type': step.step_type,
                'label': step.get_step_type_display(),
                'completed': step.completed,
            }
            for step in steps
        ]
    })
