from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
import datetime

from loyalty.models import LoyaltyProgram, LoyaltyCard, StampHistory, Reward


@login_required
def overview(request):
    merchant = request.user.merchant_profile
    program = getattr(merchant, 'program', None)

    stats = {}
    recent_history = []
    if program:
        cards = program.cards.all()
        total_customers = cards.count()
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        stamps_this_month = StampHistory.objects.filter(
            card__program=program,
            stamped_at__gte=month_start
        ).count()

        rewards_unlocked = Reward.objects.filter(card__program=program).count()
        rewards_redeemed = Reward.objects.filter(card__program=program, redeemed=True).count()

        recent_history = StampHistory.objects.filter(
            card__program=program
        ).select_related('card').order_by('-stamped_at')[:8]

        stats = {
            'total_customers': total_customers,
            'stamps_this_month': stamps_this_month,
            'rewards_unlocked': rewards_unlocked,
            'rewards_redeemed': rewards_redeemed,
        }

        pending_rewards = Reward.objects.filter(
            card__program=program, redeemed=False
        ).select_related('card').order_by('-unlocked_at')

    return render(request, 'dashboard/overview.html', {
        'program': program,
        'stats': stats,
        'recent_history': recent_history,
        'pending_rewards': pending_rewards if program else [],
    })


@login_required
def customers(request):
    merchant = request.user.merchant_profile
    program = getattr(merchant, 'program', None)
    cards = program.cards.prefetch_related('rewards').order_by('-created_at') if program else []
    pending_rewards = Reward.objects.filter(
        card__program=program, redeemed=False
    ).select_related('card') if program else []
    return render(request, 'dashboard/customers.html', {
        'program': program,
        'cards': cards,
        'pending_rewards': pending_rewards,
    })
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def super_admin_overview(request):
    """Global dashboard for Yokal platform owner."""
    from accounts.models import MerchantProfile
    
    total_merchants = MerchantProfile.objects.all().count()
    total_cards = LoyaltyCard.objects.all().count()
    total_transactions = StampHistory.objects.all().count()
    
    recent_merchants = MerchantProfile.objects.all().order_by('-created_at')[:5]
    recent_activity = StampHistory.objects.all().select_related('card', 'card__program').order_by('-stamped_at')[:10]
    
    context = {
        'total_merchants': total_merchants,
        'total_cards': total_cards,
        'total_transactions': total_transactions,
        'recent_merchants': recent_merchants,
        'recent_activity': recent_activity,
    }
    return render(request, 'dashboard/super_admin.html', context)
