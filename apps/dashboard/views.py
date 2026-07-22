from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required as django_staff_member_required
from django.views.decorators.http import require_POST

def staff_member_required(view_func):
    return django_staff_member_required(view_func, login_url='accounts:login')

from django.contrib import messages
from django.db.models import Count, Sum
from django.conf import settings as django_settings
from django.utils import timezone
import os
import datetime

from apps.loyalty.models import CURRENCY_CHOICES, LoyaltyProgram, LoyaltyCard, StampHistory, Reward
from apps.loyalty.membership import approve_membership, reject_membership, revoke_membership
from apps.accounts.models import MerchantProfile
from apps.accounts.decorators import merchant_admin_required
from apps.dashboard.utils import get_current_program, SESSION_PROGRAM_KEY
from apps.billing.views import billing, billing_checkout, billing_success, billing_cancel
from apps.billing.decorators import subscription_required, subscription_read_only


def _merchant_context(request):
    merchant = request.user.merchant_profile
    program, programs = get_current_program(request, merchant)
    return merchant, program, programs


@login_required
@subscription_read_only
def overview(request):
    merchant, program, programs = _merchant_context(request)

    # Check if onboarding is needed for new merchants
    from apps.accounts.models_onboarding import OnboardingProgress
    progress, created = OnboardingProgress.objects.get_or_create(merchant=merchant)
    
    # Redirect to onboarding if not completed and merchant is new (no cards yet)
    # TEMPORAIREMENT DÉSACTIVÉ - La redirection forcée vers l'onboarding est désactivée pour permettre l'accès libre au tableau de bord.
    # if progress.percentage < 100 and (not program or program.cards.count() == 0):
    #     return redirect('dashboard:onboarding')

    stats = {
        'total_customers': 0,
        'transactions_today': 0,
        'stamps_today': 0,
        'rewards_today': 0,
    }
    daily_transactions = []
    recent_cards = []
    
    if program:
        cards = program.cards.all()
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # 1. Top Metrics
        total_customers = cards.count()
        
        today_history = StampHistory.objects.filter(
            card__program=program,
            stamped_at__gte=today_start
        )
        transactions_today = today_history.count()
        stamps_today = today_history.aggregate(total=Sum('amount'))['total'] or 0
        
        rewards_today = Reward.objects.filter(
            card__program=program,
            unlocked_at__gte=today_start
        ).count()

        stats = {
            'total_customers': total_customers,
            'transactions_today': transactions_today,
            'stamps_today': stamps_today,
            'rewards_today': rewards_today,
        }

        # 2. Activity Lists
        daily_transactions = today_history.select_related('card').order_by('-stamped_at')[:10]
        recent_cards = cards.order_by('-created_at')[:5]

    return render(request, 'dashboard/overview.html', {
        'program': program,
        'stats': stats,
        'daily_transactions': daily_transactions,
        'recent_cards': recent_cards,
    })


@login_required
@subscription_read_only
def customers(request):
    merchant, program, programs = _merchant_context(request)

    cards = []
    total_customers = 0
    avg_stamps = 0
    ready_rewards_count = 0
    pending_rewards = []
    pending_cards = []
    status_filter = request.GET.get('status', 'approved')

    pending_cards = LoyaltyCard.objects.filter(
        program__merchant=merchant,
        membership_status='pending',
        is_deleted=False,
    ).select_related('program').order_by('-created_at')

    if program:
        if status_filter == 'pending':
            cards = pending_cards
        else:
            cards_qs = program.cards.filter(is_deleted=False).select_related('program').prefetch_related('rewards')
            if status_filter == 'all':
                cards = cards_qs.order_by('-created_at')
            else:
                cards = cards_qs.filter(membership_status='approved').order_by('-created_at')

        total_customers = cards_qs.filter(membership_status='approved').count()

        approved_cards = cards_qs.filter(membership_status='approved')
        if approved_cards.exists():
            total_stamps = sum(card.stamp_count for card in approved_cards)
            avg_stamps = round(total_stamps / approved_cards.count(), 1)

        ready_rewards_count = sum(1 for card in approved_cards if card.is_reward_ready)

        pending_rewards = Reward.objects.filter(
            card__program=program, redeemed=False
        ).select_related('card')

    return render(request, 'dashboard/customers.html', {
        'program': program,
        'cards': cards,
        'total_customers': total_customers,
        'avg_stamps': avg_stamps,
        'ready_rewards_count': ready_rewards_count,
        'pending_rewards': pending_rewards,
        'pending_cards': pending_cards,
        'status_filter': status_filter,
        'pending_count': pending_cards.count(),
    })


@login_required
@require_POST
@subscription_required
def approve_membership_view(request, token):
    merchant = request.user.merchant_profile
    card = get_object_or_404(
        LoyaltyCard,
        qr_token=token,
        program__merchant=merchant,
        is_deleted=False,
    )
    approve_membership(card, request.user)
    messages.success(request, f"Adhésion de {card.customer_name} approuvée.")
    return redirect(request.POST.get('next') or 'dashboard:customers')


@login_required
@require_POST
@subscription_required
def reject_membership_view(request, token):
    merchant = request.user.merchant_profile
    card = get_object_or_404(
        LoyaltyCard,
        qr_token=token,
        program__merchant=merchant,
        is_deleted=False,
    )
    reject_membership(card)
    messages.success(request, f"Demande de {card.customer_name} refusée.")
    return redirect(request.POST.get('next') or 'dashboard:customers')


@login_required
@require_POST
@subscription_required
def revoke_membership_view(request, token):
    merchant = request.user.merchant_profile
    card = get_object_or_404(
        LoyaltyCard,
        qr_token=token,
        program__merchant=merchant,
        is_deleted=False,
    )
    revoke_membership(card)
    messages.success(request, f"Adhésion de {card.customer_name} révoquée.")
    return redirect(request.POST.get('next') or 'dashboard:customers')


@login_required
def scanner(request):
    return redirect('loyalty:stamp_scanner')


@login_required
@subscription_read_only
def stats(request):
    merchant, program, programs = _merchant_context(request)
    
    if not program:
        return render(request, 'dashboard/stats.html', {'program': None})
    
    now = timezone.now()
    period = request.GET.get('period', '30')
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    
    # Define period delta
    if period == '1': # Aujourd'hui
        days = 1
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == '7':
        days = 7
        start_date = now - datetime.timedelta(days=7)
    elif period == '90':
        days = 90
        start_date = now - datetime.timedelta(days=90)
    elif period == '365':
        days = 365
        start_date = now - datetime.timedelta(days=365)
    elif period == 'custom' and start_str and end_str:
        try:
            start_date = datetime.datetime.strptime(start_str, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_str, '%Y-%m-%d')
            # Make dates aware if timezone is active
            if django_settings.USE_TZ:
                start_date = timezone.make_aware(start_date)
                end_date = timezone.make_aware(end_date.replace(hour=23, minute=59, second=59))
            days = (end_date - start_date).days + 1
            now = end_date # For evolution chart logic
        except ValueError:
            days = 30
            start_date = now - datetime.timedelta(days=30)
            period = '30'
    else: # Default 30
        days = 30
        period = '30'
        start_date = now - datetime.timedelta(days=30)

    if period != 'custom':
        end_date = now
    
    prev_start_date = start_date - datetime.timedelta(days=days)
    
    # 1. Basic Stats
    cards = program.cards.all()
    total_customers = cards.count()
    
    # New clients comparison
    new_clients_current = cards.filter(created_at__gte=start_date).count()
    new_clients_prev = cards.filter(created_at__range=(prev_start_date, start_date)).count()
    
    if new_clients_prev > 0:
        new_clients_diff = ((new_clients_current - new_clients_prev) / new_clients_prev) * 100
    else:
        new_clients_diff = 100 if new_clients_current > 0 else 0
        
    total_transactions = StampHistory.objects.filter(card__program=program, stamped_at__gte=start_date).count()
    rewards_count = Reward.objects.filter(card__program=program, unlocked_at__gte=start_date).count()
    
    # 2. Client Segmentation (detailed for drawer)
    from django.db.models import Max, Sum, Count
    card_activity = StampHistory.objects.filter(card__program=program).values('card').annotate(last_activity=Max('stamped_at'))
    last_activity_map = {item['card']: item['last_activity'] for item in card_activity}
    
    segments = {'active': [], 'hibernating': [], 'inactive': [], 'lost': []}
    
    for card in cards:
        last_date = last_activity_map.get(card.id)
        if not last_date:
            segments['lost'].append(card)
            continue
            
        diff_days = (now - last_date).days
        if diff_days < 7:
            segments['active'].append(card)
        elif diff_days < 30:
            segments['hibernating'].append(card)
        elif diff_days < 90:
            segments['inactive'].append(card)
        else:
            segments['lost'].append(card)

    segment_counts = {k: len(v) for k, v in segments.items()}
    segment_total = sum(segment_counts.values()) or 1
    segments_pct = {k: (v / segment_total) * 100 for k, v in segment_counts.items()}

    # 3. Points & Advanced Metrics
    total_points_period = StampHistory.objects.filter(
        card__program=program, stamped_at__gte=start_date
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    avg_points_client = round(float(total_points_period) / total_customers, 1) if total_customers > 0 else 0
    points_accumulated = StampHistory.objects.filter(card__program=program).aggregate(total=Sum('amount'))['total'] or 0
    
    # Completion Rate: % of cards with at least one reward
    cards_with_reward = cards.annotate(num_rewards=Count('rewards')).filter(num_rewards__gt=0).count()
    completion_rate = round((cards_with_reward / total_customers * 100), 1) if total_customers > 0 else 0
    
    # Average Reward Time (days)
    reward_records = Reward.objects.filter(card__program=program).select_related('card')
    if reward_records.exists():
        time_diffs = []
        for r in reward_records:
            time_diffs.append((r.unlocked_at - r.card.created_at).total_seconds())
        avg_reward_time = round(sum(time_diffs) / len(time_diffs) / 86400, 1)
    else:
        avg_reward_time = 0

    # 4. Charts Data
    # Evolution Chart
    daily_activity = []
    for i in range(0, days):
        day = now - datetime.timedelta(days=i)
        d_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        d_end = d_start + datetime.timedelta(days=1)
        
        stamps = StampHistory.objects.filter(card__program=program, stamped_at__gte=d_start, stamped_at__lt=d_end).count()
        new_c = cards.filter(created_at__gte=d_start, created_at__lt=d_end).count()
        rew = Reward.objects.filter(card__program=program, unlocked_at__gte=d_start, unlocked_at__lt=d_end).count()
        
        daily_activity.append({
            'date': day.strftime('%d/%m'),
            'stamps': stamps,
            'new_clients': new_c,
            'rewards': rew
        })
    daily_activity.reverse()

    # Busiest Hours
    from django.db.models.functions import ExtractHour, ExtractWeekDay
    hourly = StampHistory.objects.filter(card__program=program, stamped_at__gte=start_date).annotate(
        hour=ExtractHour('stamped_at')
    ).values('hour').annotate(count=Count('id')).order_by('hour')
    hour_data = [0] * 24
    for h in hourly:
        if h['hour'] is not None:
            hour_data[h['hour']] = h['count']

    # Busiest Days
    daily_dist = StampHistory.objects.filter(card__program=program, stamped_at__gte=start_date).annotate(
        weekday=ExtractWeekDay('stamped_at')
    ).values('weekday').annotate(count=Count('id')).order_by('weekday')
    # Django 1=Sun, 2=Mon...
    weekday_data = [0] * 7
    for d in daily_dist:
        if d['weekday'] is not None:
            weekday_data[d['weekday'] - 1] = d['count']

    # Top 10 Clients
    top_clients = cards.order_by('-balance')[:10]

    context = {
        'program': program,
        'period': period,
        'total_customers': total_customers,
        'new_clients_current': new_clients_current,
        'new_clients_diff': round(new_clients_diff, 1),
        'total_transactions': total_transactions,
        'rewards_count': rewards_count,
        'segments': segment_counts,
        'segments_pct': segments_pct,
        'segment_members': segments, # For drawer
        'total_points_period': total_points_period,
        'avg_points_client': avg_points_client,
        'points_accumulated': points_accumulated,
        'completion_rate': completion_rate,
        'cards_with_reward_count': cards_with_reward,
        'avg_reward_time': avg_reward_time,
        'daily_activity': daily_activity,
        'hour_data': hour_data,
        'weekday_data': weekday_data,
        'top_clients': top_clients,
    }
    
    return render(request, 'dashboard/stats.html', context)


@login_required
@subscription_read_only
def transactions(request):
    merchant, program, programs = _merchant_context(request)

    if not program:
        return render(request, 'dashboard/transactions.html', {'program': None})

    # Date navigation
    date_str = request.GET.get('date')
    try:
        current_date = datetime.date.fromisoformat(date_str) if date_str else timezone.localdate()
    except (ValueError, TypeError):
        current_date = timezone.localdate()

    prev_date = current_date - datetime.timedelta(days=1)
    next_date = current_date + datetime.timedelta(days=1)
    today = timezone.localdate()

    # Get all transactions for the selected day
    day_start = timezone.make_aware(datetime.datetime.combine(current_date, datetime.time.min))
    day_end   = timezone.make_aware(datetime.datetime.combine(current_date, datetime.time.max))

    all_txs = StampHistory.objects.filter(
        card__program=program,
        stamped_at__range=(day_start, day_end)
    ).select_related('card').order_by('-stamped_at')

    # Filter tab
    tx_filter = request.GET.get('filter', 'all')
    if tx_filter == 'stamps':
        transactions_qs = all_txs.filter(amount__gt=0)
    elif tx_filter == 'rewards':
        transactions_qs = all_txs.filter(amount=0)
    else:
        transactions_qs = all_txs

    # Daily stats
    total_transactions = all_txs.count()
    stamps_given = all_txs.filter(amount__gt=0).count()
    rewards_redeemed = Reward.objects.filter(
        card__program=program,
        redeemed_at__range=(day_start, day_end)
    ).count()

    return render(request, 'dashboard/transactions.html', {
        'program': program,
        'transactions': transactions_qs,
        'current_date': current_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'today': today,
        'tx_filter': tx_filter,
        'total_transactions': total_transactions,
        'stamps_given': stamps_given,
        'rewards_redeemed': rewards_redeemed,
    })


@login_required
def notifications(request):
    merchant, program, programs = _merchant_context(request)
    
    if not program:
        return render(request, 'dashboard/notifications.html', {'program': None})
    
    pending_rewards = Reward.objects.filter(
        card__program=program, redeemed=False
    ).select_related('card').order_by('-unlocked_at')
    
    return render(request, 'dashboard/notifications.html', {
        'program': program,
        'pending_rewards': pending_rewards,
    })


def _normalize_hex_color(value, fallback='#3b82f6'):
    if not value:
        return fallback
    v = value.strip().lstrip('#')
    if len(v) == 3:
        v = ''.join(c * 2 for c in v)
    if len(v) == 6 and all(c in '0123456789abcdefABCDEF' for c in v):
        return f'#{v.lower()}'
    return fallback


@login_required
@merchant_admin_required
def merchant_settings(request):
    merchant, program, programs = _merchant_context(request)

    def settings_redirect(tab):
        url = f"{request.path}?tab={tab}"
        if program:
            url += f"&program={program.id}"
        return redirect(url)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'commerce':
            merchant.business_name = request.POST.get('business_name')
            new_slug = request.POST.get('slug', '').strip()
            
            # Generate slug from business_name if not provided
            if not new_slug:
                from django.utils.text import slugify
                new_slug = slugify(merchant.business_name)
            
            # Check if slug is unique
            base_slug = new_slug
            counter = 1
            while MerchantProfile.objects.filter(slug=new_slug).exclude(id=merchant.id).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            
            merchant.slug = new_slug

            if request.POST.get('delete_logo') == '1':
                if merchant.logo:
                    merchant.logo.delete(save=False)
                merchant.logo = None

            elif 'logo' in request.FILES:
                merchant.logo = request.FILES['logo']

            merchant.save()

            return settings_redirect('commerce')

        elif form_type == 'membership':
            merchant.require_membership_approval = request.POST.get('require_membership_approval') == 'on'
            merchant.save(update_fields=['require_membership_approval'])
            messages.success(request, "Paramètres d'adhésion mis à jour.")
            return settings_redirect('partage')
            
        elif form_type == 'programme' and program:
            program.reward_description = request.POST.get('reward_description')
            currency = request.POST.get('currency', 'XOF')
            valid_codes = {code for code, _ in CURRENCY_CHOICES}
            if currency in valid_codes:
                program.currency = currency
            ends_at_raw = request.POST.get('ends_at', '').strip()
            if ends_at_raw:
                from django.utils.dateparse import parse_datetime
                parsed = parse_datetime(ends_at_raw)
                if not parsed:
                    try:
                        parsed = datetime.datetime.strptime(ends_at_raw, '%Y-%m-%d')
                        parsed = timezone.make_aware(parsed.replace(hour=23, minute=59, second=59))
                    except ValueError:
                        parsed = None
                program.ends_at = parsed
            else:
                program.ends_at = None
            program.expire_if_needed()
            program.save()
            messages.success(request, "Programme mis à jour.")
            return settings_redirect('programme')
            
        elif form_type == 'design' and program:
            color_p = request.POST.get('color_primary')
            color_s = request.POST.get('color_secondary')
            is_solid = request.POST.get('color_solid') == 'on'
            
            # Custom HTML fields
            program.use_custom_design = request.POST.get('use_custom_design') == 'on'
            program.custom_html = request.POST.get('custom_html', '')
            
            # Advanced design fields
            program.gradient_direction = request.POST.get('gradient_direction', '135deg')
            program.gradient_intensity = int(request.POST.get('gradient_intensity', 50))
            program.font_family = request.POST.get('font_family', 'sans-serif')
            program.font_size = request.POST.get('font_size', 'medium')
            program.font_style = request.POST.get('font_style', 'normal')
            
            if color_p:
                program.color_primary = _normalize_hex_color(color_p, program.color_primary)
                if is_solid:
                    program.color_secondary = program.color_primary
                elif color_s:
                    program.color_secondary = _normalize_hex_color(color_s, program.color_secondary)
                program.save()
            else:
                program.save()
            return settings_redirect('design')

        elif form_type == 'api_generate':
            merchant.generate_api_key()
            messages.success(request, "Clé API générée avec succès.")
            return settings_redirect('api')

        elif form_type == 'api_revoke':
            merchant.revoke_api_key()
            messages.success(request, "Clé API révoquée.")
            return settings_redirect('api')

        elif form_type == 'whatsapp':
            # WhatsApp is now managed via dedicated views in accounts/views_whatsapp.py
            # Only handle the enabled toggle here if needed
            merchant.whatsapp_enabled = request.POST.get('whatsapp_enabled') == 'on'
            merchant.save(update_fields=['whatsapp_enabled'])
            messages.success(request, "Paramètres WhatsApp mis à jour.")
            return settings_redirect('whatsapp')

    preset_colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#64748b", "#111827"]

    # Get team members for the merchant
    from apps.accounts.models import TeamMember
    team_members = TeamMember.objects.filter(merchant=merchant).order_by('-invitation_sent_at', '-joined_at')

    return render(request, 'dashboard/settings.html', {
        'program': program,
        'merchant': merchant,
        'preset_colors': preset_colors,
        'currency_choices': CURRENCY_CHOICES,
        'team_members': team_members,
    })


@login_required
@merchant_admin_required
def account(request):
    merchant, program, programs = _merchant_context(request)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'profile':
            request.user.first_name = request.POST.get('first_name')
            request.user.last_name = request.POST.get('last_name')
            request.user.save()
            phone_prefix = request.POST.get('phone_prefix', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            if phone_prefix and phone_number:
                merchant.phone = f"{phone_prefix}{phone_number}"
                merchant.save(update_fields=['phone'])
            return redirect(f"{request.path}?tab=profil")

    from apps.billing.services import ensure_merchant_subscription
    from apps.billing.models import SubscriptionPayment

    subscription = ensure_merchant_subscription(merchant)
    if subscription:
        subscription.mark_past_due_if_needed()
    payments = SubscriptionPayment.objects.filter(merchant=merchant, status='completed').select_related('plan')[:5]

    return render(request, 'dashboard/account.html', {
        'program': program,
        'subscription': subscription,
        'payments': payments,
    })


@login_required
def help_page(request):
    merchant, program, programs = _merchant_context(request)
    return render(request, 'dashboard/help.html', {'program': program})


@staff_member_required
def super_admin_overview(request):
    """Global dashboard for Yokalma platform owner."""
    from apps.loyalty.models import Currency
    from apps.billing.models import MerchantSubscription, SubscriptionPayment
    
    total_merchants = MerchantProfile.objects.all().count()
    total_cards = LoyaltyCard.objects.all().count()
    total_transactions = StampHistory.objects.all().count()
    
    # Calculate volume of transactions (sum of all stamp history amounts)
    total_volume = StampHistory.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate cards created today for trend
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cards_today = LoyaltyCard.objects.filter(created_at__gte=today_start).count()
    
    # ─── KPI: MRR (Monthly Recurring Revenue) ───
    current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    active_subscriptions = MerchantSubscription.objects.filter(
        status='active',
        current_period_end__gte=timezone.now()
    ).select_related('plan')
    mrr = sum(sub.plan.price for sub in active_subscriptions)
    
    # ─── KPI: Churn Rate (last 30 days) ───
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    canceled_subscriptions = MerchantSubscription.objects.filter(
        status='canceled',
        updated_at__gte=thirty_days_ago
    ).count()
    total_active_thirty_days_ago = MerchantSubscription.objects.filter(
        updated_at__gte=thirty_days_ago
    ).count()
    churn_rate = (canceled_subscriptions / total_active_thirty_days_ago * 100) if total_active_thirty_days_ago > 0 else 0
    
    # ─── KPI: Active Cards (cards with activity in last 30 days) ───
    active_cards = LoyaltyCard.objects.filter(
        history__stamped_at__gte=thirty_days_ago
    ).distinct().count()
    
    # ─── KPI: Stamps per day (average last 7 days) ───
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    stamps_last_7_days = StampHistory.objects.filter(
        stamped_at__gte=seven_days_ago
    ).count()
    stamps_per_day = stamps_last_7_days / 7
    
    recent_merchants = MerchantProfile.objects.all().order_by('-created_at')[:5]
    recent_activity = StampHistory.objects.all().select_related('card', 'card__program', 'card__program__merchant').order_by('-stamped_at')[:10]
    
    active_currencies = Currency.objects.filter(is_active=True)
    
    context = {
        'admin_active': 'overview',
        'total_merchants': total_merchants,
        'total_cards': total_cards,
        'total_transactions': total_transactions,
        'total_volume': total_volume,
        'cards_today': cards_today,
        'recent_merchants': recent_merchants,
        'recent_activity': recent_activity,
        'active_currencies': active_currencies,
        # KPIs
        'mrr': mrr,
        'churn_rate': round(churn_rate, 1),
        'active_cards': active_cards,
        'stamps_per_day': round(stamps_per_day, 1),
        'active_subscriptions_count': active_subscriptions.count(),
    }
    return render(request, 'dashboard/admin/overview.html', context)


@staff_member_required
def admin_marchands(request):
    from apps.loyalty.models import Currency
    search_query = request.GET.get('q', '').strip()
    merchants_qs = MerchantProfile.objects.all().order_by('-created_at')
    if search_query:
        merchants_qs = merchants_qs.filter(business_name__icontains=search_query)

    # Annotate card count
    for m in merchants_qs:
        m.card_count = LoyaltyCard.objects.filter(program__merchant=m).count()

    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    first_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    context = {
        'admin_active': 'marchands',
        'merchants': merchants_qs,
        'search_query': search_query,
        'total_merchants': MerchantProfile.objects.count(),
        'active_count': MerchantProfile.objects.filter(api_key_active=True).count(),
        'total_cards': LoyaltyCard.objects.count(),
        'new_this_month': MerchantProfile.objects.filter(created_at__gte=first_of_month).count(),
    }
    return render(request, 'dashboard/admin/marchands.html', context)


@staff_member_required
def admin_marchand_detail(request, merchant_id):
    merchant = get_object_or_404(MerchantProfile, id=merchant_id)
    programs = merchant.programs.all().select_related('currency')
    recent_cards = LoyaltyCard.objects.filter(program__merchant=merchant).order_by('-created_at')[:10]
    total_cards = LoyaltyCard.objects.filter(program__merchant=merchant).count()
    total_transactions = StampHistory.objects.filter(card__program__merchant=merchant).count()

    context = {
        'admin_active': 'marchands',
        'merchant': merchant,
        'programs': programs,
        'recent_cards': recent_cards,
        'total_cards': total_cards,
        'total_transactions': total_transactions,
    }
    return render(request, 'dashboard/admin/marchand_detail.html', context)


@staff_member_required
def admin_devises(request):
    from apps.loyalty.models import Currency
    if request.method == 'POST':
        toggle_id = request.POST.get('toggle_id')
        if toggle_id:
            c = Currency.objects.filter(id=toggle_id).first()
            if c:
                c.is_active = not c.is_active
                c.save()
                messages.success(request, f"Devise {c.code} {'activée' if c.is_active else 'désactivée'}.")
        else:
            code = request.POST.get('code', '').strip().upper()
            name = request.POST.get('name', '').strip()
            symbol = request.POST.get('symbol', '').strip()
            if code and name and symbol:
                _, created = Currency.objects.get_or_create(code=code, defaults={'name': name, 'symbol': symbol, 'is_active': True})
                if created:
                    messages.success(request, f"Devise {code} ajoutée.")
                else:
                    messages.error(request, f"La devise {code} existe déjà.")
        return redirect('admin_devises')

    currencies = Currency.objects.all().order_by('code')
    return render(request, 'dashboard/admin/devises.html', {
        'admin_active': 'devises',
        'currencies': currencies,
    })


@staff_member_required
def admin_logs(request):
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    first_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    logs = StampHistory.objects.all().select_related('card', 'card__program', 'card__program__merchant').order_by('-stamped_at')[:100]
    total_volume = StampHistory.objects.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'admin_active': 'logs',
        'logs': logs,
        'total_logs': StampHistory.objects.count(),
        'today_logs': StampHistory.objects.filter(stamped_at__gte=today_start).count(),
        'month_logs': StampHistory.objects.filter(stamped_at__gte=first_of_month).count(),
        'total_volume': total_volume,
    }
    return render(request, 'dashboard/admin/logs.html', context)


@staff_member_required
def admin_integrations(request):
    from apps.loyalty.models import LoyaltyCard
    context = {
        'admin_active': 'integrations',
        'wallet_issuer_id': getattr(django_settings, 'GOOGLE_WALLET_ISSUER_ID', ''),
        'wallet_linked_count': LoyaltyCard.objects.filter(google_wallet_linked=True).count(),
        'evolution_url': getattr(django_settings, 'EVOLUTION_API_URL', ''),
        'whatsapp_connected_count': MerchantProfile.objects.filter(whatsapp_connected=True).count(),
        'whatsapp_enabled_count': MerchantProfile.objects.filter(whatsapp_enabled=True).count(),
    }
    return render(request, 'dashboard/admin/integrations.html', context)


@staff_member_required
def admin_abonnements(request):
    from apps.billing.models import SubscriptionPlan, MerchantSubscription
    from apps.billing.services import ensure_merchant_subscription, send_renewal_notification, seed_default_plans
    from apps.loyalty.models import LoyaltyCard

    if not SubscriptionPlan.objects.exists():
        seed_default_plans()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_plan':
            max_cards = request.POST.get('max_cards', '').strip()
            max_programs = request.POST.get('max_programs', '').strip()
            SubscriptionPlan.objects.create(
                name=request.POST.get('name', '').strip(),
                slug=request.POST.get('slug', '').strip(),
                price=int(request.POST.get('price', 0) or 0),
                max_cards=int(max_cards) if max_cards else None,
                max_programs=int(max_programs) if max_programs else None,
                includes_api=bool(request.POST.get('includes_api')),
                includes_whatsapp_unlimited=bool(request.POST.get('includes_whatsapp_unlimited')),
                includes_google_wallet=bool(request.POST.get('includes_google_wallet')),
                is_popular=bool(request.POST.get('is_popular')),
                is_active=True,
                features=[f.strip() for f in request.POST.get('features', '').split('\n') if f.strip()],
            )
            messages.success(request, 'Plan créé avec succès.')
            return redirect('admin_abonnements')

        if action == 'delete_plan':
            plan = get_object_or_404(SubscriptionPlan, id=request.POST.get('plan_id'))
            if plan.is_trial:
                messages.error(request, 'Le plan Essai ne peut pas être supprimé.')
            else:
                plan.is_active = False
                plan.save(update_fields=['is_active'])
                messages.success(request, f'Plan « {plan.name} » désactivé.')
            return redirect('admin_abonnements')

        if action == 'notify_renewal':
            sub = get_object_or_404(MerchantSubscription, id=request.POST.get('subscription_id'))
            if send_renewal_notification(sub):
                messages.success(request, f'Notification envoyée à {sub.merchant.business_name}.')
            else:
                messages.warning(request, 'Impossible d\'envoyer la notification (email manquant).')
            return redirect('admin_abonnements')

    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order')
    merchants = MerchantProfile.objects.select_related('subscription__plan', 'user').order_by('-created_at')

    for m in merchants:
        m.card_count = LoyaltyCard.objects.filter(program__merchant=m).count()
        if not hasattr(m, 'subscription') or m.subscription is None:
            ensure_merchant_subscription(m)
            m.refresh_from_db()

    subscriptions = MerchantSubscription.objects.select_related('merchant', 'plan').order_by('-updated_at')

    context = {
        'admin_active': 'abonnements',
        'plans': plans,
        'merchants': merchants,
        'subscriptions': subscriptions,
        'compliant_count': sum(1 for s in subscriptions if s.is_compliant),
        'past_due_count': sum(1 for s in subscriptions if not s.is_compliant),
    }
    return render(request, 'dashboard/admin/abonnements.html', context)


@staff_member_required
def admin_parametres(request):
    from django.contrib.auth.models import User
    from apps.loyalty.models import Currency, LoyaltyCard
    context = {
        'admin_active': 'parametres',
        'total_merchants': MerchantProfile.objects.count(),
        'total_cards': LoyaltyCard.objects.count(),
        'total_transactions': StampHistory.objects.count(),
        'total_currencies': Currency.objects.filter(is_active=True).count(),
        'wallet_count': LoyaltyCard.objects.filter(google_wallet_linked=True).count(),
        'staff_users': User.objects.filter(is_staff=True).order_by('-last_login'),
    }
    return render(request, 'dashboard/admin/parametres.html', context)




@login_required
def customer_detail_ajax(request, card_id):
    merchant = request.user.merchant_profile
    card = get_object_or_404(LoyaltyCard, qr_token=card_id, program__merchant=merchant)
    
    # 1. Transaction History (StampHistory)
    history_qs = card.history.all().order_by('-stamped_at')[:20]
    history = [{
        'amount': float(h.amount),
        'date': h.stamped_at.strftime('%d %b %Y'),
        'time': h.stamped_at.strftime('%H:%M'),
        'note': h.note or ""
    } for h in history_qs]
    
    # 2. Rewards
    rewards_qs = card.rewards.all().order_by('-unlocked_at')
    rewards = [{
        'id': r.id,
        'redeemed': r.redeemed,
        'unlocked_at': r.unlocked_at.strftime('%d %b %Y'),
        'redeemed_at': r.redeemed_at.strftime('%d %b %Y') if r.redeemed_at else None
    } for r in rewards_qs]
    
    data = {
        'id': str(card.qr_token),
        'customer_name': card.customer_name,
        'customer_phone': card.customer_phone,
        'customer_email': getattr(card, 'customer_email', ""),
        'created_at': card.created_at.strftime('%d %b %Y'),
        'balance': float(card.balance),
        'total_accumulated': float(card.total_accumulated),
        'progress_percent': card.progress_percent,
        'threshold': card.program.reward_threshold,
        'unit_label': card.program.unit_label,
        'history': history,
        'rewards': rewards,
        'total_transactions': card.history.count(),
        'rewards_redeemed_count': card.rewards.filter(redeemed=True).count(),
    }
    
    return JsonResponse(data)


@login_required
def programs(request):
    """Liste et gestion des programmes de fidélité du marchand."""
    merchant, program, _ = _merchant_context(request)
    all_programs = merchant.programs.filter(active=True).order_by('-created_at')
    for p in all_programs:
        p.expire_if_needed()
    program_rows = []
    for p in all_programs:
        program_rows.append({
            'program': p,
            'clients_count': p.cards.filter(is_deleted=False).count(),
            'is_active': program and p.id == program.id,
            'is_running': p.active and not p.is_expired,
        })

    return render(request, 'dashboard/programs.html', {
        'program': program,
        'program_rows': program_rows,
    })


@login_required
def switch_program(request):
    """Change le programme actif (session) et redirige."""
    merchant = request.user.merchant_profile
    program_id = request.GET.get('program')
    next_url = request.GET.get('next') or '/dashboard/'
    selected = merchant.get_program(program_id)
    if selected:
        request.session[SESSION_PROGRAM_KEY] = selected.id
    return redirect(next_url)
