import secrets
import uuid
from django.db import models
from django.contrib.auth.models import User


CURRENCY_CHOICES = [
    ('XOF', 'Franc CFA Ouest africain 🇸🇳'),
    ('EUR', 'Euro 🇪🇺'),
    ('USD', 'Dollar américain 🇺🇸'),
]

CURRENCY_SYMBOLS = {
    'XOF': 'FCFA',
    'EUR': '€',
    'USD': '$',
}


class Currency(models.Model):
    code = models.CharField(max_length=3, choices=CURRENCY_CHOICES, primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Nom de la devise")
    symbol = models.CharField(max_length=5, verbose_name="Symbole")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Devise"
        verbose_name_plural = "Devises"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} — {self.name}"


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

    merchant = models.ForeignKey(
        'accounts.MerchantProfile',
        on_delete=models.CASCADE,
        related_name='programs',
        verbose_name='Commerçant',
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
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='XOF',
        verbose_name="Devise de base",
        help_text="La devise utilisée pour le programme",
    )
    description = models.TextField(blank=True, verbose_name="Description du programme")
    reward_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0,
        verbose_name="Valeur de la récompense (en devise de base)",
        help_text="Valeur estimée de la récompense en devise de base",
    )
    active = models.BooleanField(default=True)
    ends_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Date de fin du programme",
        help_text="À cette date le programme est désactivé. Les cartes clients sont conservées.",
    )
    google_wallet_class_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Custom HTML Design
    use_custom_design = models.BooleanField(default=False, verbose_name="Utiliser un design HTML personnalisé")
    custom_html = models.TextField(
        blank=True, 
        verbose_name="Code HTML personnalisé",
        help_text="Utilisez {name}, {phone}, {balance}, {total}, {logo} comme variables."
    )
    
    # Advanced Design Options
    gradient_direction = models.CharField(
        max_length=20, 
        default='135deg',
        choices=[
            ('135deg', 'Diagonal (↘)'),
            ('90deg', 'Horizontal (→)'),
            ('180deg', 'Vertical (↓)'),
            ('45deg', 'Diagonal inverse (↗)'),
            ('radial', 'Radial (○)'),
        ],
        verbose_name="Direction du dégradé"
    )
    gradient_intensity = models.PositiveIntegerField(
        default=50,
        verbose_name="Intensité du dégradé",
        help_text="Intensité de l'effet de dégradé (0-100)"
    )
    font_family = models.CharField(
        max_length=20,
        default='sans-serif',
        choices=[
            ('sans-serif', 'Sans-serif'),
            ('serif', 'Serif'),
            ('monospace', 'Monospace'),
            ('cursive', 'Cursive'),
        ],
        verbose_name="Police du titre"
    )
    font_size = models.CharField(
        max_length=10,
        default='medium',
        choices=[
            ('small', 'Petit'),
            ('medium', 'Moyen'),
            ('large', 'Grand'),
        ],
        verbose_name="Taille du texte"
    )
    font_style = models.CharField(
        max_length=10,
        default='normal',
        choices=[
            ('normal', 'Normal'),
            ('italic', 'Italique'),
            ('bold', 'Gras'),
        ],
        verbose_name="Style du texte"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Programme de fidélité"

    def __str__(self):
        return f"{self.name} — {self.merchant.business_name}"

    @property
    def is_expired(self):
        from django.utils import timezone
        if not self.ends_at:
            return False
        return timezone.now() >= self.ends_at

    def expire_if_needed(self):
        from django.utils import timezone
        if self.ends_at and timezone.now() >= self.ends_at and self.active:
            self.active = False
            self.save(update_fields=['active', 'updated_at'])
            return True
        return False

    @property
    def currency_symbol(self):
        return CURRENCY_SYMBOLS.get(self.currency, self.currency)

    @property
    def unit_label(self):
        if self.program_type == 'visits':
            return "Tampon" if self.reward_threshold <= 1 else "Tampons"
        elif self.program_type == 'points':
            return "Point" if self.reward_threshold <= 1 else "Points"
        return self.currency_symbol


class LoyaltyCard(models.Model):
    MEMBERSHIP_STATUS = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Refusé'),
        ('revoked', 'Révoqué'),
    ]

    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='cards')
    customer_name = models.CharField(max_length=150, verbose_name="Nom du client")
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    customer_email = models.EmailField(blank=True, max_length=254, verbose_name="Email")
    membership_status = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_STATUS,
        default='approved',
        verbose_name="Statut d'adhésion",
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Approuvé le")
    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_memberships',
        verbose_name="Approuvé par",
    )
    
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
    apple_wallet_serial_number = models.CharField(max_length=255, blank=True, null=True)
    apple_wallet_linked = models.BooleanField(default=False)
    wallet_url = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Carte de fidélité"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            name_part = slugify(f"{self.program.name}-{self.customer_name}")
            # Ensure we have at least something if names are empty or weird
            if not name_part:
                name_part = "carte"
            token_part = str(self.qr_token)[:6]
            self.slug = f"{name_part}-{token_part}"
        
        # Track previous balance for reward detection
        track_reward = False
        if self.pk:
            try:
                old_card = LoyaltyCard.objects.get(pk=self.pk)
                self._old_balance = old_card.balance
                track_reward = True
            except LoyaltyCard.DoesNotExist:
                self._old_balance = 0
        else:
            self._old_balance = 0
        
        super().save(*args, **kwargs)
        
        # Auto-create reward if threshold reached
        if track_reward and self.is_reward_ready and self._old_balance < self.program.reward_threshold:
            self._auto_create_reward()

    def __str__(self):
        return f"{self.customer_name} — {self.program.name}"

    @property
    def is_membership_usable(self):
        return (
            self.membership_status == 'approved'
            and self.is_active
            and not self.is_deleted
        )

    @property
    def is_pending_membership(self):
        return self.membership_status == 'pending'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('loyalty:customer_card', args=[self.slug or str(self.qr_token)])

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

    def _auto_create_reward(self):
        """Automatically create a reward when threshold is reached."""
        # Check if reward already exists and not redeemed
        existing_reward = Reward.objects.filter(
            card=self,
            redeemed=False
        ).first()
        
        if existing_reward:
            return  # Reward already exists
        
        # Create new reward
        Reward.objects.create(
            card=self,
            description=self.program.reward_description,
            value=self.program.reward_value
        )


class StampHistory(models.Model):
    """Renamed conceptually to TransactionHistory in the future, keeping name for now."""
    TRANSACTION_TYPES = [
        ('add', 'Ajout'),
        ('subtract', 'Déduction'),
        ('redeem', 'Récompense'),
        ('refund', 'Remboursement'),
    ]

    card = models.ForeignKey(LoyaltyCard, on_delete=models.CASCADE, related_name='history')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=1.0, verbose_name="Valeur")
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES, default='add',
        verbose_name="Type de transaction",
    )
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
    code = models.CharField(max_length=20, unique=True, editable=False, default='')
    unlocked_at = models.DateTimeField(auto_now_add=True)
    redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Récompense"
        ordering = ['-unlocked_at']

    def save(self, *args, **kwargs):
        if not self.code:
            for _ in range(10):
                candidate = secrets.token_hex(6).upper()
                if not Reward.objects.filter(code=candidate).exists():
                    self.code = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        status = "✓ Utilisée" if self.redeemed else "En attente"
        return f"{self.card.customer_name} — {status}"


class ProgramTemplate(models.Model):
    """Pre-configured loyalty program templates."""
    BUSINESS_TYPES = [
        ('bakery', 'Boulangerie'),
        ('hair_salon', 'Coiffure'),
        ('cafe', 'Café'),
        ('restaurant', 'Restaurant'),
        ('retail', 'Commerce de détail'),
        ('gym', 'Salle de sport'),
        ('car_wash', 'Lavage auto'),
    ]
    
    business_type = models.CharField(
        max_length=20,
        choices=BUSINESS_TYPES,
        unique=True,
        verbose_name="Type de commerce"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nom du template"
    )
    description = models.TextField(
        verbose_name="Description"
    )
    program_type = models.CharField(
        max_length=20,
        choices=[('visits', 'Visites'), ('points', 'Points')],
        default='visits',
        verbose_name="Type de programme"
    )
    reward_threshold = models.PositiveIntegerField(
        default=10,
        verbose_name="Seuil pour récompense"
    )
    reward_description = models.CharField(
        max_length=255,
        default="1 article offert",
        verbose_name="Description de la récompense"
    )
    reward_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Valeur de la récompense"
    )
    unit_label = models.CharField(
        max_length=20,
        default="Tampon",
        verbose_name="Libellé de l'unité"
    )
    color_primary = models.CharField(
        max_length=7,
        default='#0E0F0D',
        verbose_name="Couleur principale"
    )
    color_secondary = models.CharField(
        max_length=7,
        default='#D4FF4E',
        verbose_name="Couleur secondaire"
    )
    card_template = models.CharField(
        max_length=20,
        choices=[
            ('classic', 'Classique'),
            ('glass', 'Verre'),
            ('bold', 'Bold'),
            ('luxury', 'Luxe'),
        ],
        default='classic',
        verbose_name="Modèle de carte"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Template de programme"
        verbose_name_plural = "Templates de programmes"

    def __str__(self):
        return f"{self.name} ({self.get_business_type_display()})"

    def apply_to_program(self, program):
        """Apply template settings to a loyalty program."""
        program.program_type = self.program_type
        program.reward_threshold = self.reward_threshold
        program.reward_description = self.reward_description
        program.reward_value = self.reward_value
        program.unit_label = self.unit_label
        program.color_primary = self.color_primary
        program.color_secondary = self.color_secondary
        program.card_template = self.card_template
        program.save()
        return program


# Import referral models at the end to avoid circular imports
from .models_referral import ReferralCode, Referral
