"""
Referral system for loyalty program.
Allows customers to refer friends and earn bonus stamps.
"""

from django.db import models
from django.utils import timezone
import uuid


class ReferralCode(models.Model):
    """Unique referral code for a customer."""
    card = models.OneToOneField(
        'LoyaltyCard',
        on_delete=models.CASCADE,
        related_name='referral_code',
        verbose_name="Carte du parrain"
    )
    code = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        verbose_name="Code de parrainage"
    )
    uses_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre d'utilisations"
    )
    max_uses = models.PositiveIntegerField(
        default=10,
        verbose_name="Utilisations maximales"
    )
    bonus_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.0,
        verbose_name="Bonus par parrainage"
    )
    active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'expiration"
    )

    class Meta:
        verbose_name = "Code de parrainage"
        verbose_name_plural = "Codes de parrainage"

    def __str__(self):
        return f"{self.code} - {self.card.customer_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()
        super().save(*args, **kwargs)

    def _generate_code(self):
        """Generate a unique referral code."""
        while True:
            code = ''.join([
                str(uuid.uuid4()).replace('-', '')[:8].upper()
            ])
            if not ReferralCode.objects.filter(code=code).exists():
                return code

    def is_valid(self):
        """Check if referral code is valid for use."""
        if not self.active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.uses_count >= self.max_uses:
            return False
        return True


class Referral(models.Model):
    """Record of a successful referral."""
    referral_code = models.ForeignKey(
        ReferralCode,
        on_delete=models.CASCADE,
        related_name='referrals',
        verbose_name="Code de parrainage utilisé"
    )
    referred_card = models.ForeignKey(
        'LoyaltyCard',
        on_delete=models.CASCADE,
        related_name='referrals_received',
        verbose_name="Carte du filleul"
    )
    bonus_given = models.BooleanField(
        default=False,
        verbose_name="Bonus accordé"
    )
    bonus_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Montant du bonus"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Parrainage"
        verbose_name_plural = "Parrainages"
        unique_together = ['referral_code', 'referred_card']

    def __str__(self):
        return f"{self.referral_code.card.customer_name} → {self.referred_card.customer_name}"
