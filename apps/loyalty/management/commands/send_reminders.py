from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.loyalty.models import LoyaltyCard
from apps.accounts.models import MerchantProfile
from apps.loyalty.whatsapp_service import WhatsAppService


class Command(BaseCommand):
    help = 'Envoyer des rappels WhatsApp aux clients inactifs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Jours d\'inactivité avant envoi du rappel (défaut: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler l\'envoi sans envoyer réellement'
        )

    def handle(self, *args, **options):
        days_inactive = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days_inactive)
        
        self.stdout.write(f"🔍 Recherche des clients inactifs depuis {days_inactive} jours...")
        
        # Trouver les cartes avec numéro de téléphone
        cards_with_phone = LoyaltyCard.objects.filter(
            customer_phone__isnull=False,
            customer_phone__ne='',
            is_deleted=False,
            program__active=True
        ).select_related('program', 'program__merchant')
        
        reminders_sent = 0
        reminders_skipped = 0
        
        for card in cards_with_phone:
            # Vérifier la dernière activité
            last_stamp = card.history.order_by('-stamped_at').first()
            
            if not last_stamp:
                # Carte jamais tamponnée - ignorer
                continue
            
            days_since_last_visit = (timezone.now() - last_stamp.stamped_at).days
            
            if days_since_last_visit >= days_inactive:
                # Vérifier si le marchand a WhatsApp activé
                merchant = card.program.merchant
                if not merchant.whatsapp_connected or not merchant.whatsapp_enabled:
                    reminders_skipped += 1
                    continue
                
                # Vérifier si le client est proche d'une récompense
                remaining = card.remaining_to_reward
                is_close_to_reward = remaining <= 2
                
                # Construire le message
                if is_close_to_reward:
                    message = (
                        f"👋 Bonjour {card.customer_name} !\n\n"
                        f"Ça fait un moment que nous ne vous avons pas vu chez {merchant.business_name} !\n\n"
                        f"🎉 Bonne nouvelle : il vous reste seulement {remaining} {card.program.unit_label} "
                        f"pour votre récompense ({card.program.reward_description}) !\n\n"
                        f"À très bientôt !"
                    )
                else:
                    message = (
                        f"👋 Bonjour {card.customer_name} !\n\n"
                        f"Ça fait un moment que nous ne vous avons pas vu chez {merchant.business_name} !\n\n"
                        f"Votre solde actuel : {card.balance} {card.program.unit_label}\n"
                        f"Seuil pour récompense : {card.program.reward_threshold} {card.program.unit_label}\n\n"
                        f"À très bientôt !"
                    )
                
                if dry_run:
                    self.stdout.write(f"[DRY RUN] Rappel pour {card.customer_name} ({card.customer_phone})")
                    reminders_sent += 1
                else:
                    try:
                        # Envoyer le message WhatsApp
                        success = WhatsAppService.send_text_message(
                            merchant.whatsapp_instance_id,
                            card.customer_phone,
                            message,
                            merchant=merchant
                        )
                        
                        if success:
                            self.stdout.write(
                                self.style.SUCCESS(f"✅ Rappel envoyé à {card.customer_name}")
                            )
                            reminders_sent += 1
                        else:
                            self.stdout.write(
                                self.style.ERROR(f"❌ Échec envoi à {card.customer_name}")
                            )
                            reminders_skipped += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Erreur pour {card.customer_name}: {e}")
                        )
                        reminders_skipped += 1
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f"📊 Résumé :")
        self.stdout.write(f"   Rappels envoyés : {reminders_sent}")
        self.stdout.write(f"   Rappels ignorés : {reminders_skipped}")
        self.stdout.write('='*50)
