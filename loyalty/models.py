import uuid
from django.db import models
from django.contrib.auth.models import User


class LoyaltyProgram(models.Model):
    PROGRAM_TYPES = [
        ('visits', 'Nombre de visites (Tampons)'),
        ('points', 'Points cumulés'),
        ('spend', 'Montant dépensé'),
    ]

    CARD_TEMPLATES = [
        ('classic', 'Classique (Épuré)'),
        ('glass', 'Vitre (Glassmorphism)'),
        ('bold', 'Bold (Urbain & Impactant)'),
        ('luxury', 'Luxe (Sérif & Élégance)'),
    ]

    merchant = models.OneToOneField(
        'accounts.MerchantProfile',
        on_delete=models.CASCADE,
        related_name='program'
    )
    name = models.CharField(max_length=150, verbose_name="Nom du programme")
    program_type = models.CharField(
        max_length=20, choices=PROGRAM_TYPES, default='visits',
        verbose_name="Type de programme"
    )
    card_template = models.CharField(
        max_length=20, choices=CARD_TEMPLATES, default='classic',
        verbose_name="Modèle de carte"
    )
    
    # Configuration for points/spend
    points_per_unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=1.0,
        verbose_name="Points par unité (visite ou 1000 XAF)",
        help_text="Pour 'visites', mettre 1. Pour 'montant', points pour chaque 1000 XAF par exemple."
    )
    
    reward_threshold = models.PositiveIntegerField(
        default=10, verbose_name="Seuil pour une récompense",
        help_text="Nombre de tampons ou points nécessaires."
    )
    
    color_primary = models.CharField(max_length=7, default='#0E0F0D', verbose_name="Couleur principale")
    color_secondary = models.CharField(max_length=7, default='#D4FF4E', verbose_name="Couleur secondaire")
    logo = models.ImageField(upload_to='programs/logos/', blank=True, null=True)
    
    reward_description = models.CharField(
        max_length=255, default="1 article offert",
        verbose_name="Description de la récompense"
    )
    active = models.BooleanField(default=True)
    google_wallet_class_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Programme de fidélité"

    def __str__(self):
        return f"{self.name} — {self.merchant.business_name}"

    @property
    def unit_label(self):
        if self.program_type == 'visits':
            return "Tampon" if self.reward_threshold <= 1 else "Tampons"
        elif self.program_type == 'points':
            return "Point" if self.reward_threshold <= 1 else "Points"
        return "XAF"


class LoyaltyCard(models.Model):
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='cards')
    customer_name = models.CharField(max_length=150, verbose_name="Nom du client")
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    
    # Generic balance
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Solde actuel")
    total_accumulated = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="Cumul total")
    
    # Keep old fields as properties for backward compatibility if needed, or just migrate
    @property
    def stamp_count(self):
        return int(self.balance)
    
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    google_wallet_object_id = models.CharField(max_length=255, blank=True)
    google_wallet_linked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Carte de fidélité"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} — {self.program.name}"

    @property
    def progress_percent(self):
        if self.program.reward_threshold == 0:
            return 100
        return min(100, int((float(self.balance) / self.program.reward_threshold) * 100))

    @property
    def remaining_to_reward(self):
        return max(0, float(self.program.reward_threshold) - float(self.balance))

    @property
    def is_reward_ready(self):
        return float(self.balance) >= float(self.program.reward_threshold)


class StampHistory(models.Model):
    """Renamed conceptually to TransactionHistory in the future, keeping name for now."""
    card = models.ForeignKey(LoyaltyCard, on_delete=models.CASCADE, related_name='history')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=1.0, verbose_name="Valeur")
    stamped_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Enregistré par"
    )
    note = models.CharField(max_length=200, blank=True, verbose_name="Note")
    stamped_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historique Transaction"
        ordering = ['-stamped_at']

    def __str__(self):
        return f"{self.card.customer_name} — {self.amount} {self.card.program.unit_label}"


class Reward(models.Model):
    card = models.ForeignKey(LoyaltyCard, on_delete=models.CASCADE, related_name='rewards')
    unlocked_at = models.DateTimeField(auto_now_add=True)
    redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Récompense"
        ordering = ['-unlocked_at']

    def __str__(self):
        status = "✓ Utilisée" if self.redeemed else "En attente"
        return f"{self.card.customer_name} — {status}"
