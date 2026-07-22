"""
Referral system views.
"""

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.loyalty.models import LoyaltyCard, ReferralCode, Referral
from apps.accounts.utils import get_merchant


@login_required
@require_POST
def generate_referral_code(request, card_id):
    """Generate a referral code for a customer card."""
    merchant = get_merchant(request.user)
    if not merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    card = get_object_or_404(LoyaltyCard, pk=card_id, program__merchant=merchant)
    
    # Check if referral code already exists
    if hasattr(card, 'referral_code'):
        return JsonResponse({
            'success': True,
            'code': card.referral_code.code,
            'uses_count': card.referral_code.uses_count,
            'max_uses': card.referral_code.max_uses,
        })
    
    # Create new referral code
    referral_code = ReferralCode.objects.create(card=card)
    
    return JsonResponse({
        'success': True,
        'code': referral_code.code,
        'uses_count': referral_code.uses_count,
        'max_uses': referral_code.max_uses,
    })


@login_required
@require_POST
def apply_referral_code(request):
    """Apply a referral code when creating a new card."""
    code = request.POST.get('referral_code', '').strip().upper()
    
    if not code:
        return JsonResponse({'error': 'Code de parrainage requis'}, status=400)
    
    # Find the referral code
    try:
        referral_code = ReferralCode.objects.get(code=code)
    except ReferralCode.DoesNotExist:
        return JsonResponse({'error': 'Code de parrainage invalide'}, status=400)
    
    # Check if code is valid
    if not referral_code.is_valid():
        return JsonResponse({'error': 'Code de parrainage expiré ou invalide'}, status=400)
    
    # Get the card being created (assuming it's in the session or form data)
    # This would need to be integrated with the new_card view
    # For now, return success
    return JsonResponse({
        'success': True,
        'bonus_amount': referral_code.bonus_amount,
        'message': f'Code valide ! Vous recevrez {referral_code.bonus_amount} points bonus.'
    })


@login_required
def referral_stats(request):
    """Get referral statistics for the merchant."""
    merchant = get_merchant(request.user)
    if not merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    from apps.dashboard.utils import get_current_program
    program, _ = get_current_program(request, merchant)
    
    if not program:
        return JsonResponse({'error': 'Aucun programme trouvé'}, status=404)
    
    # Get referral stats
    total_codes = ReferralCode.objects.filter(card__program=program).count()
    total_referrals = Referral.objects.filter(referral_code__card__program=program).count()
    
    return JsonResponse({
        'total_codes': total_codes,
        'total_referrals': total_referrals,
    })
