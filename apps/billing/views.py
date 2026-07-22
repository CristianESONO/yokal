import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.decorators import merchant_admin_required
from apps.billing.models import SubscriptionPayment, SubscriptionPlan
from apps.billing.paytech import PaytechService
from apps.billing.services import (
    cancel_payment,
    complete_payment,
    create_checkout_payment,
    ensure_merchant_subscription,
)

logger = logging.getLogger(__name__)


@login_required
@merchant_admin_required
def billing(request):
    merchant = request.user.merchant_profile
    subscription = ensure_merchant_subscription(merchant)
    if subscription:
        subscription.mark_past_due_if_needed()

    plans = SubscriptionPlan.objects.filter(is_active=True, is_trial=False).order_by('sort_order')
    payments = SubscriptionPayment.objects.filter(merchant=merchant).select_related('plan')[:20]
    paytech_ready = PaytechService.is_configured()

    return render(request, 'dashboard/billing.html', {
        'subscription': subscription,
        'plans': plans,
        'payments': payments,
        'paytech_ready': paytech_ready,
    })


@login_required
@merchant_admin_required
@require_POST
def billing_checkout(request, plan_id):
    merchant = request.user.merchant_profile
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True, is_trial=False)
    subscription = ensure_merchant_subscription(merchant)

    payment_type = 'renewal'
    if subscription and subscription.plan_id == plan.id and subscription.is_compliant:
        messages.info(request, 'Vous êtes déjà abonné à ce plan.')
        return redirect('dashboard:billing')

    if subscription and subscription.status == 'trialing':
        payment_type = 'subscription'

    redirect_url, error = create_checkout_payment(merchant, plan, payment_type=payment_type)
    if error:
        messages.error(request, error)
        return redirect('dashboard:billing')

    return redirect(redirect_url)


@login_required
def billing_success(request):
    messages.success(request, 'Paiement en cours de validation. Votre abonnement sera activé sous peu.')
    return redirect('dashboard:billing')


@login_required
def billing_cancel(request):
    messages.warning(request, 'Paiement annulé.')
    return redirect('dashboard:billing')


@csrf_exempt
@require_POST
def paytech_ipn(request):
    if not PaytechService.verify_ipn(request.POST):
        logger.warning('PayTech IPN rejected — invalid signature')
        return HttpResponse('IPN KO', status=403)

    type_event = request.POST.get('type_event')
    ref_command = request.POST.get('ref_command', '')

    try:
        payment = SubscriptionPayment.objects.get(ref_command=ref_command)
    except SubscriptionPayment.DoesNotExist:
        logger.error('PayTech IPN: payment not found for %s', ref_command)
        return HttpResponse('IPN OK', status=200)

    ipn_data = {k: request.POST.get(k) for k in request.POST}

    if type_event == 'sale_complete':
        complete_payment(payment, ipn_data)
    elif type_event == 'sale_canceled':
        cancel_payment(payment, ipn_data)

    return HttpResponse('IPN OK', status=200)
