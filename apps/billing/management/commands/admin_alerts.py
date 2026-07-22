from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import MerchantProfile
from apps.billing.models import SubscriptionPayment, MerchantSubscription
from apps.loyalty.models import StampHistory


class Command(BaseCommand):
    help = 'Génère les alertes admin pour les paiements échoués et marchands inactifs'

    def handle(self, *args, **options):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # ─── Alert 1: Paiements échoués (last 7 days) ───
        seven_days_ago = now - timedelta(days=7)
        failed_payments = SubscriptionPayment.objects.filter(
            status='failed',
            created_at__gte=seven_days_ago
        ).select_related('merchant', 'plan')
        
        # ─── Alert 2: Marchands inactifs (30+ days sans activité) ───
        inactive_merchants = []
        for merchant in MerchantProfile.objects.all():
            last_activity = StampHistory.objects.filter(
                card__program__merchant=merchant
            ).order_by('-stamped_at').first()
            
            if last_activity:
                days_since_activity = (now - last_activity.stamped_at).days
                if days_since_activity >= 30:
                    inactive_merchants.append({
                        'merchant': merchant,
                        'days_inactive': days_since_activity,
                        'last_activity': last_activity.stamped_at,
                    })
            else:
                # Marchand sans aucune activité
                days_since_creation = (now - merchant.created_at).days
                if days_since_creation >= 30:
                    inactive_merchants.append({
                        'merchant': merchant,
                        'days_inactive': days_since_creation,
                        'last_activity': None,
                    })
        
        # ─── Alert 3: Abonnements expirés non renouvelés ───
        expired_subscriptions = MerchantSubscription.objects.filter(
            status__in=['expired', 'past_due'],
            current_period_end__lt=now
        ).select_related('merchant', 'plan')
        
        # ─── Output ───
        self.stdout.write(self.style.WARNING('=== ALERTES ADMIN YOKALMA ===\n'))
        
        if failed_payments.exists():
            self.stdout.write(self.style.ERROR(f'🔴 {failed_payments.count()} paiement(s) échoué(s) (7 derniers jours)'))
            for payment in failed_payments:
                self.stdout.write(f'  - {payment.merchant.business_name}: {payment.amount} {payment.currency} ({payment.ref_command})')
        else:
            self.stdout.write(self.style.SUCCESS('✅ Aucun paiement échoué (7 derniers jours)'))
        
        self.stdout.write('')
        
        if inactive_merchants:
            self.stdout.write(self.style.WARNING(f'🟡 {len(inactive_merchants)} marchand(s) inactif(s) (30+ jours)'))
            for item in inactive_merchants:
                last = item['last_activity'].strftime('%d/%m/%Y') if item['last_activity'] else 'Jamais'
                self.stdout.write(f'  - {item["merchant"].business_name}: inactif depuis {item["days_inactive"]} jours (dernière activité: {last})')
        else:
            self.stdout.write(self.style.SUCCESS('✅ Aucun marchand inactif (30+ jours)'))
        
        self.stdout.write('')
        
        if expired_subscriptions.exists():
            self.stdout.write(self.style.ERROR(f'🔴 {expired_subscriptions.count()} abonnement(s) expiré(s) non renouvelé(s)'))
            for sub in expired_subscriptions:
                self.stdout.write(f'  - {sub.merchant.business_name}: {sub.plan.name} (expiré le {sub.current_period_end.strftime("%d/%m/%Y")})')
        else:
            self.stdout.write(self.style.SUCCESS('✅ Aucun abonnement expiré non renouvelé'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== FIN DES ALERTES ==='))
