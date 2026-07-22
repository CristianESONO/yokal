from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from apps.loyalty.stamp_logic import compute_stamp_amount
from apps.loyalty.models import LoyaltyProgram, LoyaltyCard, StampHistory, Reward
from apps.loyalty.membership import enroll_customer
from apps.wallet.services import update_loyalty_object
from .auth import api_key_required, json_body


def _program_for_merchant(merchant, program_id=None):
    if program_id:
        return merchant.programs.filter(id=program_id, active=True).first()
    return merchant.programs.filter(active=True).order_by('-created_at').first()


def _card_json(card):
    return {
        'id': str(card.qr_token),
        'customer_name': card.customer_name,
        'customer_phone': card.customer_phone,
        'balance': float(card.balance),
        'total_accumulated': float(card.total_accumulated),
        'reward_threshold': card.program.reward_threshold,
        'progress_percent': card.progress_percent,
        'is_reward_ready': card.is_reward_ready,
        'program_id': card.program_id,
        'program_name': card.program.name,
        'created_at': card.created_at.isoformat(),
    }


@csrf_exempt
@api_key_required
@require_http_methods(['GET'])
def list_programs(request):
    programs = request.merchant.programs.filter(active=True)
    return JsonResponse({
        'programs': [{
            'id': p.id,
            'name': p.name,
            'program_type': p.program_type,
            'reward_threshold': p.reward_threshold,
            'reward_description': p.reward_description,
            'points_per_unit': float(p.points_per_unit),
        } for p in programs]
    })


@csrf_exempt
@api_key_required
@require_http_methods(['GET'])
def list_customers(request):
    program_id = request.GET.get('program_id')
    program = _program_for_merchant(request.merchant, program_id)
    if not program:
        return JsonResponse({'error': 'Programme introuvable.'}, status=404)

    cards = program.cards.all().order_by('-created_at')
    return JsonResponse({
        'program_id': program.id,
        'customers': [_card_json(c) for c in cards],
    })


@csrf_exempt
@api_key_required
@require_http_methods(['GET'])
def get_customer(request, token):
    card = LoyaltyCard.objects.filter(
        qr_token=token,
        program__merchant=request.merchant,
    ).select_related('program').first()
    if not card:
        return JsonResponse({'error': 'Client introuvable.'}, status=404)

    pending_rewards = card.rewards.filter(redeemed=False).count()
    return JsonResponse({
        **_card_json(card),
        'pending_rewards': pending_rewards,
        'card_url': request.build_absolute_uri(f'/card/{card.qr_token}/'),
    })


@csrf_exempt
@api_key_required
@require_http_methods(['POST'])
def create_customer(request):
    data = json_body(request)
    if data is None:
        return JsonResponse({'error': 'Corps JSON invalide.'}, status=400)

    program_id = data.get('program_id')
    program = _program_for_merchant(request.merchant, program_id)
    if not program:
        return JsonResponse({'error': 'Programme introuvable.'}, status=404)

    name = (data.get('customer_name') or '').strip()
    if not name:
        return JsonResponse({'error': 'customer_name est requis.'}, status=400)

    phone = (data.get('customer_phone') or '').strip()
    if phone:
        existing = LoyaltyCard.objects.filter(program=program, customer_phone=phone).first()
        if existing:
            return JsonResponse({'customer': _card_json(existing), 'created': False})

    # TEMPORAIREMENT DÉSACTIVÉ - Limite de cartes désactivée
    # from apps.billing.services import ensure_merchant_subscription
    # sub = ensure_merchant_subscription(request.merchant)
    # if sub and sub.plan.max_cards is not None:
    #     current_cards = LoyaltyCard.objects.filter(program__merchant=request.merchant).count()
    #     if current_cards >= sub.plan.max_cards:
    #         return JsonResponse({'error': f'Limite de cartes clients atteinte pour votre forfait ({sub.plan.max_cards}).'}, status=403)

    card, created = enroll_customer(
        program,
        customer_name=name,
        customer_phone=phone,
        auto_approve=True,
    )
    return JsonResponse({'customer': _card_json(card), 'created': created}, status=201 if created else 200)


@csrf_exempt
@api_key_required
@require_http_methods(['POST'])
def stamp_customer(request, token):
    card = LoyaltyCard.objects.filter(
        qr_token=token,
        program__merchant=request.merchant,
    ).select_related('program').first()
    if not card:
        return JsonResponse({'error': 'Client introuvable.'}, status=404)

    if not card.is_membership_usable:
        return JsonResponse({'error': 'Adhésion non validée ou révoquée.'}, status=403)

    data = json_body(request) or {}
    try:
        amount = compute_stamp_amount(card.program, data.get('amount'))
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    card.balance = float(card.balance) + amount
    card.total_accumulated = float(card.total_accumulated) + amount
    card.save()

    StampHistory.objects.create(card=card, amount=amount, note=data.get('note', ''))

    reward_unlocked = False
    threshold = float(card.program.reward_threshold)
    rewards_created = []
    while float(card.balance) >= threshold:
        reward = Reward.objects.create(card=card)
        card.balance = float(card.balance) - threshold
        card.save()
        reward_unlocked = True
        rewards_created.append({'id': reward.id, 'code': reward.code})

    update_loyalty_object(card)

    return JsonResponse({
        'success': True,
        'customer': _card_json(card),
        'reward_unlocked': reward_unlocked,
        'rewards_created': rewards_created,
    })


@csrf_exempt
@api_key_required
@require_http_methods(['POST'])
def redeem_reward(request, reward_id):
    reward = Reward.objects.filter(
        id=reward_id,
        card__program__merchant=request.merchant,
        redeemed=False,
    ).select_related('card').first()
    if not reward:
        return JsonResponse({'error': 'Récompense introuvable ou déjà utilisée.'}, status=404)

    reward.redeemed = True
    reward.redeemed_at = timezone.now()
    reward.save()

    return JsonResponse({
        'success': True,
        'reward_id': reward.id,
        'code': reward.code,
        'customer_name': reward.card.customer_name,
    })
