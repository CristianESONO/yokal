from datetime import timedelta

from django.db import models
from django.utils import timezone


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    currency = models.CharField(max_length=3, default='XOF')
    billing_period_days = models.PositiveIntegerField(default=30)
    max_cards = models.PositiveIntegerField(null=True, blank=True, help_text='Vide = illimité')
    max_programs = models.PositiveIntegerField(null=True, blank=True, help_text='Vide = illimité')
    includes_api = models.BooleanField(default=False)
    includes_whatsapp_unlimited = models.BooleanField(default=False)
    includes_google_wallet = models.BooleanField(default=False)
    is_trial = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    features = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'price']

    def __str__(self):
        return self.name

    @property
    def is_free(self):
        return self.price == 0

    @property
    def cards_label(self):
        return str(self.max_cards) if self.max_cards else 'Illimité'

    @property
    def programs_label(self):
        return str(self.max_programs) if self.max_programs else 'Illimité'


class MerchantSubscription(models.Model):
    STATUS_CHOICES = [
        ('trialing', 'Essai'),
        ('active', 'Actif'),
        ('past_due', 'En retard'),
        ('expired', 'Expiré'),
        ('canceled', 'Annulé'),
    ]

    merchant = models.OneToOneField(
        'accounts.MerchantProfile',
        on_delete=models.CASCADE,
        related_name='subscription',
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trialing')
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    renewal_notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Abonnement marchand'

    def __str__(self):
        return f'{self.merchant.business_name} — {self.plan.name}'

    @property
    def is_compliant(self):
        now = timezone.now()
        if self.status == 'active':
            return bool(self.current_period_end and self.current_period_end > now)
        if self.status == 'trialing':
            return bool(self.trial_ends_at and self.trial_ends_at > now)
        return False

    @property
    def renewal_date(self):
        if self.status == 'trialing':
            return self.trial_ends_at
        return self.current_period_end

    @property
    def days_until_renewal(self):
        end = self.renewal_date
        if not end:
            return None
        delta = end - timezone.now()
        return max(0, delta.days)

    def mark_past_due_if_needed(self):
        if self.is_compliant:
            return
        if self.status in ('active', 'trialing'):
            self.status = 'past_due' if self.status == 'active' else 'expired'
            self.save(update_fields=['status', 'updated_at'])

    def activate_from_payment(self, plan, period_days=None):
        now = timezone.now()
        days = period_days or plan.billing_period_days
        self.plan = plan
        self.status = 'active'
        self.current_period_start = now
        self.current_period_end = now + timedelta(days=days)
        self.renewal_notified_at = None
        self.save()

        merchant = self.merchant
        if plan.includes_api and not merchant.api_key:
            merchant.generate_api_key()
        elif plan.includes_api:
            merchant.api_key_active = True
            merchant.save(update_fields=['api_key_active'])
        elif not plan.includes_api:
            merchant.revoke_api_key()


class SubscriptionPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Payé'),
        ('failed', 'Échoué'),
        ('canceled', 'Annulé'),
    ]
    TYPE_CHOICES = [
        ('subscription', 'Souscription'),
        ('renewal', 'Renouvellement'),
    ]

    merchant = models.ForeignKey(
        'accounts.MerchantProfile',
        on_delete=models.CASCADE,
        related_name='subscription_payments',
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    currency = models.CharField(max_length=3, default='XOF')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='subscription')
    ref_command = models.CharField(max_length=100, unique=True)
    paytech_token = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=100, blank=True)
    paytech_payload = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    period_start = models.DateTimeField(null=True, blank=True)
    period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.ref_command} — {self.get_status_display()}'
