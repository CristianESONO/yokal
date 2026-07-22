from django.core.management.base import BaseCommand
from apps.loyalty.models import Currency


class Command(BaseCommand):
    help = 'Initialiser les devises dans la base de données'

    def handle(self, *args, **options):
        currencies = [
            {'code': 'XOF', 'name': 'Franc CFA Ouest africain', 'symbol': 'FCFA'},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
            {'code': 'USD', 'name': 'Dollar américain', 'symbol': '$'},
        ]

        for curr in currencies:
            _, created = Currency.objects.get_or_create(
                code=curr['code'],
                defaults={
                    'name': curr['name'],
                    'symbol': curr['symbol'],
                    'is_active': True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Créé: {curr["code"]} - {curr["name"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'Existe déjà: {curr["code"]}'))

        self.stdout.write(self.style.SUCCESS('Initialisation des devises terminée.'))
