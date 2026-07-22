import os

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import MerchantProfile
from apps.billing.models import MerchantSubscription
from apps.billing.services import ensure_merchant_subscription, seed_default_plans, send_renewal_notification


class Command(BaseCommand):
    help = 'Vérifie les abonnements expirés et envoie les rappels de renouvellement'

    def add_arguments(self, parser):
        parser.add_argument('--seed-plans', action='store_true', help='Créer les plans par défaut')
        parser.add_argument('--notify-days', type=int, default=7, help='Jours avant échéance pour notifier')

    def handle(self, *args, **options):
        if options['seed_plans']:
            seed_default_plans()
            self.stdout.write(self.style.SUCCESS('Plans par défaut créés/mis à jour.'))

        notify_days = options['notify_days']
        now = timezone.now()

        for merchant in MerchantProfile.objects.all():
            ensure_merchant_subscription(merchant)

        updated = 0
        notified = 0
        for sub in MerchantSubscription.objects.select_related('merchant', 'plan', 'merchant__user'):
            sub.mark_past_due_if_needed()
            if sub.status in ('past_due', 'expired'):
                updated += 1

            days = sub.days_until_renewal
            if days is None:
                continue
            if days > notify_days:
                continue
            if sub.renewal_notified_at and (now - sub.renewal_notified_at).days < 3:
                continue
            if send_renewal_notification(sub):
                notified += 1

        self.stdout.write(self.style.SUCCESS(
            f'Terminé — {updated} abonnement(s) en retard/expiré, {notified} notification(s) envoyée(s).'
        ))
