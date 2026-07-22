import io
import qrcode
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import LoyaltyProgram, LoyaltyCard, StampHistory, Reward
from .forms import LoyaltyProgramForm, LoyaltyCardForm
from .membership import enroll_customer
from .whatsapp_service import send_whatsapp_stamp_notification
from .stamp_logic import compute_stamp_amount, stamp_input_label, stamp_input_default
from apps.accounts.models import MerchantProfile
from apps.accounts.utils import get_merchant
from apps.wallet.services import (
    create_loyalty_class, create_loyalty_object,
    update_loyalty_object, generate_add_to_wallet_url,
    is_wallet_configured,
)
from apps.billing.decorators import subscription_required


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
    """Public page a customer sees after scanning the QR code or using a slug."""
    try:
        # Try finding by UUID (standard token)
        card = LoyaltyCard.objects.get(qr_token=token)
    except (LoyaltyCard.DoesNotExist, ValueError, ValidationError):
        # Otherwise try finding by slug (pretty URL)
        card = get_object_or_404(LoyaltyCard, slug=token)

    if card.is_deleted:
        return render(request, 'loyalty/card_unavailable.html', {
            'card': card,
            'program': card.program,
            'reason': 'deleted',
        })

    if not card.is_membership_usable:
        return render(request, 'loyalty/card_unavailable.html', {
            'card': card,
            'program': card.program,
            'reason': card.membership_status,
        })

    history = card.history.all()[:5]
    pending_rewards = card.rewards.filter(redeemed=False)

    # Show Add to Wallet button whenever Google Wallet is configured
    wallet_configured = is_wallet_configured()
    wallet_url = reverse('wallet:add_to_wallet', args=[card.qr_token]) if wallet_configured else None

    context = {
        'card': card,
        'program': card.program,
        'history': history,
        'pending_rewards': pending_rewards,
        'wallet_url': wallet_url,
        'stamps': range(int(card.program.reward_threshold)) if card.program.program_type == 'visits' else None,
    }
    return render(request, 'loyalty/card.html', context)


def self_enroll(request, program_id):
    """Page for new customers to register for a loyalty program."""
    program = get_object_or_404(LoyaltyProgram, id=program_id)
    
    # ─── SUBSCRIPTION ENFORCEMENT ───
    from apps.billing.services import ensure_merchant_subscription
    sub = ensure_merchant_subscription(program.merchant)
    subscription_invalid = False
    limit_reached = False
    
    if sub and not sub.is_compliant:
        subscription_invalid = True
    # TEMPORAIREMENT DÉSACTIVÉ - Limite de cartes désactivée
    # elif sub and sub.plan.max_cards is not None:
    #     current_cards = LoyaltyCard.objects.filter(program__merchant=program.merchant).count()
    #     if current_cards >= sub.plan.max_cards:
    #         limit_reached = True
    limit_reached = False
            
    if request.method == 'POST' and not subscription_invalid and not limit_reached:
        form = LoyaltyCardForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['customer_phone']
            existing = LoyaltyCard.objects.filter(
                program=program, customer_phone=phone, is_deleted=False
            ).first()
            if existing:
                messages.info(request, "Bienvenue ! Voici votre carte existante.")
                return redirect('loyalty:customer_card', token=str(existing.qr_token))

            card, _ = enroll_customer(
                program,
                customer_name=form.cleaned_data['customer_name'],
                customer_phone=phone,
                customer_email=form.cleaned_data.get('customer_email', ''),
            )
            if card.is_membership_usable:
                messages.success(request, "Félicitations ! Votre carte est prête.")
                return redirect('loyalty:customer_card', token=str(card.qr_token))
            messages.success(request, "Votre demande a été envoyée. Le commerce va valider votre inscription.")
            return render(request, 'loyalty/enroll_success.html', {
                'merchant': program.merchant,
                'cards': [card],
                'created_count': 1,
                'pending': True,
            })
    else:
        form = LoyaltyCardForm()
    
    context = {
        'program': program,
        'form': form,
        'is_enrollment': True,
        'subscription_invalid': subscription_invalid,
        'limit_reached': limit_reached,
        'max_cards': sub.plan.max_cards if sub else None,
    }
    return render(request, 'loyalty/enroll.html', context)


@login_required
def program_qr(request, program_id):
    """Génère le QR code PNG du lien d'inscription au programme."""
    program = get_object_or_404(
        LoyaltyProgram, id=program_id, merchant=request.user.merchant_profile
    )
    join_url = request.build_absolute_uri(
        reverse('loyalty:self_enroll', args=[program.id])
    )
    img = qrcode.make(join_url)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')


@login_required
def merchant_qr(request, merchant_slug):
    """Génère le QR code PNG du lien d'inscription global marchand."""
    merchant = get_object_or_404(MerchantProfile, slug=merchant_slug)
    if merchant.user_id != request.user.id:
        return HttpResponse(status=403)
    join_url = request.build_absolute_uri(
        reverse('loyalty:merchant_enroll', args=[merchant.slug])
    )
    img = qrcode.make(join_url)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')


def customer_qr(request, token):
    """Génère le QR code PNG pour qu'un commerçant puisse scanner la carte d'un client."""
    card = get_object_or_404(LoyaltyCard, qr_token=token)
    
    # On encode l'URL publique de la carte. 
    # - Si scanné par un marchand via le dashboard Yokalma, le scanner extraira le token.
    # - Si scanné par un mobile tiers, il ouvrira la page de la carte.
    card_url = request.build_absolute_uri(
        reverse('loyalty:customer_card', args=[card.qr_token])
    )
    
    img = qrcode.make(card_url)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')


@login_required
@require_POST
def edit_card(request, token):
    """Permet au marchand de modifier les informations d'une carte client."""
    merchant = get_merchant(request.user)
    card = get_object_or_404(LoyaltyCard, qr_token=token)
    
    if card.program.merchant != merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    card.customer_name = request.POST.get('customer_name', card.customer_name)
    card.customer_phone = request.POST.get('customer_phone', card.customer_phone)
    card.customer_email = request.POST.get('customer_email', card.customer_email)
    
    try:
        new_balance = request.POST.get('balance')
        if new_balance is not None:
            card.balance = float(new_balance)
    except ValueError:
        pass
        
    card.save()
    update_loyalty_object(card)
    
    messages.success(request, f"Informations de {card.customer_name} mises à jour.")
    return redirect('dashboard:customers')


@login_required
@require_POST
def delete_program(request, program_id):
    """Désactive un programme (soft delete). Les cartes clients sont conservées."""
    merchant = get_merchant(request.user)
    if not merchant:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard:programs')

    program = get_object_or_404(LoyaltyProgram, id=program_id, merchant=merchant)

    if not program.active:
        messages.info(request, "Ce programme est déjà désactivé.")
        return redirect('dashboard:programs')

    active_count = merchant.programs.filter(active=True).count()
    if active_count <= 1:
        messages.error(request, "Vous devez conserver au moins un programme actif.")
        return redirect('dashboard:programs')

    program.active = False
    program.save(update_fields=['active', 'updated_at'])

    session_key = 'active_program_id'
    if request.session.get(session_key) == program.id:
        next_program = merchant.programs.filter(active=True).order_by('-created_at').first()
        if next_program:
            request.session[session_key] = next_program.id
        else:
            request.session.pop(session_key, None)

    messages.success(request, f"Le programme « {program.name} » a été supprimé.")
    return redirect('dashboard:programs')


@login_required
@require_POST
def delete_card(request, token):
    """Désactive une carte client (soft delete)."""
    merchant = get_merchant(request.user)
    card = get_object_or_404(LoyaltyCard, qr_token=token)
    
    if card.program.merchant != merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    card.is_deleted = True
    card.save()
    
    messages.success(request, f"La carte de {card.customer_name} a été supprimée.")
    return redirect('dashboard:customers')


# ─────────────────────────────────────────────
#  MERCHANT VIEWS (login required)
# ─────────────────────────────────────────────

from apps.dashboard.utils import get_current_program


def _resolve_program_for_setup(request, merchant):
    """Resolve create vs edit — POST n'a pas ?new=1 dans l'URL, d'où les champs cachés."""
    create_new = (
        request.GET.get('new') == '1'
        or request.POST.get('create_new') == '1'
    )
    program_id = request.GET.get('program') or request.POST.get('program_id')
    if create_new:
        return None
    if program_id:
        return merchant.get_program(program_id)
    _, program = get_current_program(request, merchant)
    return program if program else merchant.program


@login_required
@subscription_required
def program_setup(request):
    """Create or edit a loyalty program."""
    merchant = get_merchant(request.user)
    if not merchant:
        messages.error(request, "Commerce non configuré ou non trouvé.")
        return redirect('loyalty:landing')

    program = _resolve_program_for_setup(request, merchant)

    from apps.billing.services import ensure_merchant_subscription
    sub = ensure_merchant_subscription(merchant)

    if request.method == 'POST':
        # Enforce max active programs limit if creating a new one
        if not program:
            if sub and sub.plan.max_programs is not None:
                active_programs_count = merchant.programs.filter(active=True).count()
                if active_programs_count >= sub.plan.max_programs:
                    messages.error(request, f"Limite atteinte : Votre abonnement vous limite à {sub.plan.max_programs} programme(s) actif(s).")
                    return redirect('dashboard:programs')

        form = LoyaltyProgramForm(request.POST, request.FILES, instance=program)
        if form.is_valid():
            prog = form.save(commit=False)
            prog.merchant = merchant
            prog.save()
            create_loyalty_class(prog)
            request.session['active_program_id'] = prog.id
            messages.success(request, "Programme enregistré avec succès.")
            return redirect('dashboard:programs')
        messages.error(request, "Corrigez les erreurs du formulaire avant de continuer.")
    else:
        form = LoyaltyProgramForm(instance=program)

    return render(request, 'loyalty/program_setup.html', {
        'form': form,
        'program': program,
        'programs': merchant.programs.filter(active=True),
    })


@login_required
@subscription_required
def new_card(request):
    """Create a new loyalty card for a customer."""
    merchant = get_merchant(request.user)
    if not merchant:
        messages.error(request, "Commerce non configuré ou non trouvé.")
        return redirect('loyalty:landing')

    programs = merchant.programs.filter(active=True)
    program_id = request.GET.get('program') or request.POST.get('program')
    program = merchant.get_program(program_id) if program_id else None
    if not program:
        program, _ = get_current_program(request, merchant)

    if not program:
        messages.warning(request, "Créez d'abord un programme de fidélité.")
        return redirect('loyalty:program_setup')

    from apps.billing.services import ensure_merchant_subscription
    sub = ensure_merchant_subscription(merchant)

    if request.method == 'POST':
        # TEMPORAIREMENT DÉSACTIVÉ - Limite de cartes désactivée
        # # Enforce max cards limit
        # if sub and sub.plan.max_cards is not None:
        #     current_cards = LoyaltyCard.objects.filter(program__merchant=merchant).count()
        #     if current_cards >= sub.plan.max_cards:
        #         messages.error(request, f"Limite atteinte : Votre abonnement vous limite à {sub.plan.max_cards} cartes clients.")
        #         return redirect('dashboard:billing')

        form = LoyaltyCardForm(request.POST)
        if form.is_valid():
            card, _ = enroll_customer(
                program,
                customer_name=form.cleaned_data['customer_name'],
                customer_phone=form.cleaned_data.get('customer_phone', ''),
                customer_email=form.cleaned_data.get('customer_email', ''),
                auto_approve=True,
            )
            messages.success(request, f"Carte créée pour {card.customer_name}.")
            return redirect('loyalty:customer_card', token=str(card.qr_token))
    else:
        form = LoyaltyCardForm()

    return render(request, 'loyalty/new_card.html', {
        'form': form,
        'program': program,
        'programs': programs,
    })


@login_required
@require_POST
@subscription_required
def stamp_card(request, token):
    """Add one stamp to a card. Called from the merchant's scanner or customers page."""
    merchant = get_merchant(request.user)
    if not merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)

    card = get_object_or_404(LoyaltyCard, qr_token=token)

    if card.program.merchant != merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)

    if not card.is_membership_usable:
        return JsonResponse({'error': 'Adhésion non validée ou révoquée.'}, status=403)

    try:
        amount = compute_stamp_amount(card.program, request.POST.get('amount'))
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    card.balance = float(card.balance) + amount
    card.total_accumulated = float(card.total_accumulated) + amount
    card.save()

    StampHistory.objects.create(card=card, amount=amount, stamped_by=request.user)

    reward_unlocked = False
    threshold = float(card.program.reward_threshold)
    while float(card.balance) >= threshold:
        Reward.objects.create(card=card)
        card.balance = float(card.balance) - threshold
        card.save()
        reward_unlocked = True

    update_loyalty_object(card)
    
    # Send WhatsApp notification
    send_whatsapp_stamp_notification(card, amount)

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
        messages.success(
            request,
            f"Ajout réussi pour {card.customer_name} "
            f"({card.balance}/{card.program.reward_threshold} {card.program.unit_label})"
        )

    if request.POST.get('redirect') == 'customers':
        return redirect('dashboard:customers')
    return redirect('loyalty:stamp_scanner')


@login_required
def stamp_scanner(request):
    """Merchant scanner page — shows a form to enter QR token manually."""
    merchant = get_merchant(request.user)
    if not merchant:
        return redirect('loyalty:landing')
    program, _ = get_current_program(request, merchant)
    recent_stamps = StampHistory.objects.filter(
        stamped_by=request.user
    ).select_related('card').order_by('-stamped_at')[:10]
    return render(request, 'loyalty/stamp_scanner.html', {
        'program': program,
        'recent_stamps': recent_stamps,
        'stamp_input_label': stamp_input_label(program) if program else 'Points',
        'stamp_input_default': stamp_input_default(program) if program else 1,
        'stamp_input_step': '1' if program and program.program_type != 'spend' else '100',
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