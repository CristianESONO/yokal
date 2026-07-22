from django.core.management.base import BaseCommand

from apps.loyalty.models import LoyaltyProgram


class Command(BaseCommand):
    help = 'Désactive les programmes dont la date de fin est dépassée (conserve les cartes clients)'

    def handle(self, *args, **options):
        expired = 0
        for program in LoyaltyProgram.objects.filter(active=True, ends_at__isnull=False):
            if program.expire_if_needed():
                expired += 1
                self.stdout.write(f'  Expiré : {program.name} ({program.merchant.business_name})')
        self.stdout.write(self.style.SUCCESS(f'{expired} programme(s) expiré(s).'))
