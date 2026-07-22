import uuid
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.billing.models import MerchantSubscription, SubscriptionPayment, SubscriptionPlan
from apps.billing.paytech import PaytechService


def get_trial_plan():
    return SubscriptionPlan.objects.filter(is_trial=True, is_active=True).order_by('sort_order').first()


def ensure_merchant_subscription(merchant):
    trial_plan = get_trial_plan()
    if not trial_plan:
        trial_plan = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order').first()
    if not trial_plan:
        return None

    sub, created = MerchantSubscription.objects.get_or_create(
        merchant=merchant,
        defaults={
            'plan': trial_plan,
            'status': 'trialing' if trial_plan.is_trial else 'active',
            'trial_ends_at': merchant.created_at + timedelta(days=30) if trial_plan.is_trial else None,
            'current_period_end': merchant.created_at + timedelta(days=30) if trial_plan.is_trial else None,
        },
    )
    return sub


def create_checkout_payment(merchant, plan, payment_type='subscription'):
    ref_command = f'YOKAL-{merchant.id}-{uuid.uuid4().hex[:12].upper()}'
    payment = SubscriptionPayment.objects.create(
        merchant=merchant,
        plan=plan,
        amount=plan.price,
        currency=plan.currency,
        payment_type=payment_type,
        ref_command=ref_command,
    )

    site = settings.SITE_URL.rstrip('/')
    custom_field = {
        'payment_id': payment.id,
        'merchant_id': merchant.id,
        'plan_id': plan.id,
        'payment_type': payment_type,
    }

    response = PaytechService.request_payment(
        item_name=f'Abonnement {plan.name} — Yokalma',
        item_price=plan.price,
        ref_command=ref_command,
        command_name=f'Abonnement {plan.name}',
        custom_field=custom_field,
        success_url=f'{site}/dashboard/billing/success/',
        cancel_url=f'{site}/dashboard/billing/cancel/',
        ipn_url=f'{site}/billing/paytech/ipn/',
    )

    if response.get('success') != 1:
        payment.status = 'failed'
        payment.paytech_payload = response
        payment.save(update_fields=['status', 'paytech_payload'])
        return None, response.get('message', 'Erreur PayTech')

    payment.paytech_token = response.get('token', '')
    payment.paytech_payload = response
    payment.save(update_fields=['paytech_token', 'paytech_payload'])

    redirect_url = response.get('redirect_url') or response.get('redirectUrl')
    return redirect_url, None


def complete_payment(payment, ipn_data):
    if payment.status == 'completed':
        return

    now = timezone.now()
    payment.status = 'completed'
    payment.paid_at = now
    payment.payment_method = ipn_data.get('payment_method', '')
    payment.paytech_payload = {**payment.paytech_payload, 'ipn': dict(ipn_data)}
    payment.period_start = now
    payment.period_end = now + timedelta(days=payment.plan.billing_period_days)
    payment.save()

    sub = ensure_merchant_subscription(payment.merchant)
    if sub:
        sub.activate_from_payment(payment.plan)


def cancel_payment(payment, ipn_data=None):
    payment.status = 'canceled'
    if ipn_data:
        payment.paytech_payload = {**payment.paytech_payload, 'ipn': dict(ipn_data)}
    payment.save(update_fields=['status', 'paytech_payload'])


def send_renewal_notification(subscription):
    merchant = subscription.merchant
    user = merchant.user
    if not user.email:
        return False

    end_date = subscription.renewal_date
    days = subscription.days_until_renewal
    subject = f'Yokalma — Renouvellement abonnement dans {days} jour(s)'
    message = (
        f'Bonjour {user.get_full_name() or merchant.business_name},\n\n'
        f'Votre abonnement {subscription.plan.name} arrive à échéance le '
        f'{end_date.strftime("%d/%m/%Y") if end_date else "bientôt"}.\n\n'
        f'Renouvelez dès maintenant : {settings.SITE_URL}/dashboard/billing/\n\n'
        f'— L\'équipe Yokalma'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
    subscription.renewal_notified_at = timezone.now()
    subscription.save(update_fields=['renewal_notified_at'])
    return True


def seed_default_plans():
    defaults = [
        {
            'slug': 'essai',
            'name': 'Essai',
            'price': 0,
            'max_cards': 50,
            'max_programs': 1,
            'is_trial': True,
            'sort_order': 1,
            'features': ['Scanner QR', 'WhatsApp (limité)', 'Jusqu\'à 50 cartes'],
        },
        {
            'slug': 'standard',
            'name': 'Standard',
            'price': 15000,
            'max_cards': 500,
            'max_programs': 3,
            'includes_whatsapp_unlimited': True,
            'includes_google_wallet': True,
            'is_popular': True,
            'sort_order': 2,
            'features': ['WhatsApp illimité', 'Google Wallet', 'Statistiques avancées', 'Jusqu\'à 500 cartes'],
        },
        {
            'slug': 'premium',
            'name': 'Premium',
            'price': 35000,
            'max_cards': None,
            'max_programs': None,
            'includes_api': True,
            'includes_whatsapp_unlimited': True,
            'includes_google_wallet': True,
            'sort_order': 3,
            'features': ['API complète', 'Support prioritaire', 'Cartes illimitées', 'Design personnalisé'],
        },
    ]
    for data in defaults:
        slug = data.pop('slug')
        SubscriptionPlan.objects.update_or_create(slug=slug, defaults=data)
