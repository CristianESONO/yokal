from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import LoyaltyProgram, LoyaltyCard, StampHistory, Reward
from .forms import LoyaltyProgramForm, LoyaltyCardForm
from wallet.services import (
    create_loyalty_class, create_loyalty_object,
    update_loyalty_object, generate_add_to_wallet_url
)


def landing(request):
    steps = [
        {'title': 'Créez votre compte', 'desc': 'Inscription en 2 minutes. Renseignez votre commerce, vos couleurs et votre récompense.'},
        {'title': 'Personnalisez', 'desc': 'Couleurs, logo, nombre de tampons et description de la récompense à votre image.'},
        {'title': 'Partagez', 'desc': 'Vos clients scannent le QR code et ajoutent la carte à Google Wallet instantanément.'},
    ]
    pricing_features = [
        'Clients illimités',
        'Google Wallet intégré',
        'Personnalisation complète (logo, couleurs)',
        'Dashboard analytics en temps réel',
        'Scanner QR en caisse',
        'Récompenses automatiques',
        'Historique des tampons',
    ]
    return render(request, 'landing.html', {'steps': steps, 'pricing_features': pricing_features})


# ─────────────────────────────────────────────
#  CUSTOMER VIEWS (public, mobile-first)
# ─────────────────────────────────────────────

def customer_card(request, token):
    """Public page a customer sees after scanning the QR code."""
    card = get_object_or_404(LoyaltyCard, qr_token=token)
    history = card.history.all()[:5]
    pending_rewards = card.rewards.filter(redeemed=False)
    wallet_url = generate_add_to_wallet_url(card) if not card.google_wallet_linked else None
    context = {
        'card': card,
        'program': card.program,
        'history': history,
        'pending_rewards': pending_rewards,
        'wallet_url': wallet_url,
        'stamps': range(int(card.program.reward_threshold)) if card.program.program_type == 'visits' else None,
    }
    return render(request, 'loyalty/card.html', context)


# ─────────────────────────────────────────────
#  MERCHANT VIEWS (login required)
# ─────────────────────────────────────────────

@login_required
def program_setup(request):
    """Create or edit the merchant's loyalty program."""
    merchant = request.user.merchant_profile
    program = getattr(merchant, 'program', None)

    if request.method == 'POST':
        form = LoyaltyProgramForm(request.POST, request.FILES, instance=program)
        if form.is_valid():
            prog = form.save(commit=False)
            prog.merchant = merchant
            prog.save()
            # Sync with Google Wallet
            create_loyalty_class(prog)
            messages.success(request, "Programme mis à jour avec succès.")
            return redirect('dashboard:overview')
    else:
        form = LoyaltyProgramForm(instance=program)

    return render(request, 'loyalty/program_setup.html', {'form': form, 'program': program})


@login_required
def new_card(request):
    """Create a new loyalty card for a customer."""
    merchant = request.user.merchant_profile
    program = getattr(merchant, 'program', None)
    if not program:
        messages.warning(request, "Créez d'abord votre programme de fidélité.")
        return redirect('loyalty:program_setup')

    if request.method == 'POST':
        form = LoyaltyCardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.program = program
            card.save()
            # Create Google Wallet object
            create_loyalty_object(card)
            messages.success(request, f"Carte créée pour {card.customer_name}.")
            return redirect('loyalty:customer_card', token=str(card.qr_token))
    else:
        form = LoyaltyCardForm()

    return render(request, 'loyalty/new_card.html', {'form': form, 'program': program})


@login_required
@require_POST
def stamp_card(request, token):
    """Add one stamp to a card. Called from the merchant's scanner page."""
    card = get_object_or_404(LoyaltyCard, qr_token=token)

    # Verify the card belongs to this merchant
    if card.program.merchant != request.user.merchant_profile:
        return JsonResponse({'error': 'Non autorisé'}, status=403)

    # For visits, amount is 1.0. For others, we might want to pass it via POST.
    amount = float(request.POST.get('amount', card.program.points_per_unit))
    
    card.balance = float(card.balance) + amount
    card.total_accumulated = float(card.total_accumulated) + amount
    card.save()

    StampHistory.objects.create(card=card, amount=amount, stamped_by=request.user)

    # Check for reward
    reward_unlocked = False
    if float(card.balance) >= float(card.program.reward_threshold):
        Reward.objects.create(card=card)
        card.balance = float(card.balance) - float(card.program.reward_threshold)
        card.save()
        reward_unlocked = True

    # Sync Google Wallet
    update_loyalty_object(card)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({
            'success': True,
            'balance': float(card.balance),
            'reward_unlocked': reward_unlocked,
            'customer_name': card.customer_name,
        })

    if reward_unlocked:
        messages.success(request, f"🎉 Récompense débloquée pour {card.customer_name} !")
    else:
        messages.success(request, f"Ajout réussi pour {card.customer_name} ({card.balance}/{card.program.reward_threshold} {card.program.unit_label})")

    return redirect('loyalty:stamp_scanner')


@login_required
def stamp_scanner(request):
    """Merchant scanner page — shows a form to enter QR token manually."""
    merchant = request.user.merchant_profile
    program = getattr(merchant, 'program', None)
    recent_stamps = StampHistory.objects.filter(
        stamped_by=request.user
    ).select_related('card').order_by('-stamped_at')[:10]
    return render(request, 'loyalty/stamp_scanner.html', {
        'program': program,
        'recent_stamps': recent_stamps,
    })


@login_required
@require_POST
def redeem_reward(request, reward_id):
    """Mark a reward as redeemed."""
    reward = get_object_or_404(Reward, pk=reward_id)
    if reward.card.program.merchant != request.user.merchant_profile:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    reward.redeemed = True
    reward.redeemed_at = timezone.now()
    reward.save()
    messages.success(request, f"Récompense validée pour {reward.card.customer_name}.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:overview'))
