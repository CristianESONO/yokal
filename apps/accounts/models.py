from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Import location and onboarding models
from .models_location import Location
from .models_onboarding import OnboardingStep, OnboardingProgress


class MerchantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant_profile')
    business_name = models.CharField(max_length=150, verbose_name="Nom du commerce")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="Slug")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    country = models.CharField(max_length=100, default="Sénégal", verbose_name="Pays")
    logo = models.ImageField(upload_to='merchants/logos/', blank=True, null=True, verbose_name="Logo")
    api_key = models.CharField(max_length=64, blank=True, unique=True, null=True, verbose_name="Clé API")
    api_key_active = models.BooleanField(default=False, verbose_name="Clé API active")
    api_key_last_used = models.DateTimeField(null=True, blank=True, verbose_name="Dernière utilisation API")
    
    # WhatsApp Settings (Evolution API)
    whatsapp_api_url = models.URLField(max_length=255, blank=True, null=True, verbose_name="URL Gateway WhatsApp")
    whatsapp_api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name="Clé API WhatsApp")
    whatsapp_instance_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID Instance WhatsApp")
    whatsapp_instance_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nom Instance WhatsApp")
    whatsapp_enabled = models.BooleanField(default=False, verbose_name="Notifications WhatsApp actives")
    whatsapp_connected = models.BooleanField(default=False, verbose_name="WhatsApp Connecté")
    whatsapp_last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Dernière activité WhatsApp")
    require_membership_approval = models.BooleanField(
        default=True,
        verbose_name="Validation manuelle des adhésions",
        help_text="Les clients doivent être approuvés avant d'utiliser leur carte.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil Marchand"

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.business_name)
            self.slug = base_slug
            counter = 1
            while MerchantProfile.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def program(self):
        """Programme actif par défaut (rétrocompatibilité dashboard)."""
        return self.programs.filter(active=True).order_by('-created_at').first()

    def get_program(self, program_id=None):
        if program_id:
            return self.programs.filter(id=program_id).first()
        return self.program

    def generate_api_key(self):
        import secrets
        self.api_key = secrets.token_hex(32)
        self.api_key_active = True
        self.save(update_fields=['api_key', 'api_key_active'])
        return self.api_key

    def revoke_api_key(self):
        self.api_key_active = False
        self.save(update_fields=['api_key_active'])


class TeamMember(models.Model):
    """Membres d'équipe d'un marchand"""
    ROLE_CHOICES = [
        ('member', '💳 Membre (Scanner QR + points)'),
        ('admin', '👑 Administrateur (Accès complet)'),
        ('owner', '👨‍💼 Propriétaire (Gestionnaire)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente (invitation envoyée)'),
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
    ]

    merchant = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='team_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='team_memberships')
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Pour tracker les invitations
    invitation_token = models.CharField(max_length=100, unique=True, blank=True, null=True)
    invitation_sent_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Membre d'équipe"
        ordering = ['-created_at']
        unique_together = [('merchant', 'email')]

    def __str__(self):
        return f"{self.email} - {self.merchant.business_name}"