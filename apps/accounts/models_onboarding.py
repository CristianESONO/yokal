"""
Onboarding checklist for new merchants.
Helps guide merchants through the setup process.
"""

from django.db import models
from django.utils import timezone


class OnboardingStep(models.Model):
    """Individual step in the onboarding process."""
    STEP_CHOICES = [
        ('profile', 'Compléter le profil'),
        ('program', 'Créer un programme de fidélité'),
        ('card', 'Créer la première carte'),
        ('wallet', 'Configurer Google Wallet'),
        ('whatsapp', 'Connecter WhatsApp'),
    ]
    
    merchant = models.ForeignKey(
        'MerchantProfile',
        on_delete=models.CASCADE,
        related_name='onboarding_steps',
        verbose_name="Marchand"
    )
    step_type = models.CharField(
        max_length=20,
        choices=STEP_CHOICES,
        verbose_name="Type d'étape"
    )
    completed = models.BooleanField(
        default=False,
        verbose_name="Complété"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de complétion"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Étape d'onboarding"
        verbose_name_plural = "Étapes d'onboarding"
        unique_together = ['merchant', 'step_type']

    def __str__(self):
        return f"{self.get_step_type_display()} - {'✓' if self.completed else '○'}"

    def mark_complete(self):
        """Mark the step as completed."""
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()


class OnboardingProgress(models.Model):
    """Track overall onboarding progress for a merchant."""
    merchant = models.OneToOneField(
        'MerchantProfile',
        on_delete=models.CASCADE,
        related_name='onboarding_progress',
        verbose_name="Marchand"
    )
    current_step = models.CharField(
        max_length=20,
        choices=OnboardingStep.STEP_CHOICES,
        default='profile',
        verbose_name="Étape actuelle"
    )
    percentage = models.PositiveIntegerField(
        default=0,
        verbose_name="Pourcentage de complétion"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Progression d'onboarding"
        verbose_name_plural = "Progressions d'onboarding"

    def __str__(self):
        return f"{self.merchant.business_name} - {self.percentage}%"

    def update_progress(self):
        """Recalculate progress percentage."""
        total_steps = len(OnboardingStep.STEP_CHOICES)
        completed_steps = self.merchant.onboarding_steps.filter(completed=True).count()
        self.percentage = int((completed_steps / total_steps) * 100)
        
        # Update current step
        for step_type, _ in OnboardingStep.STEP_CHOICES:
            step = self.merchant.onboarding_steps.filter(step_type=step_type).first()
            if step and not step.completed:
                self.current_step = step_type
                break
        
        # Check if all steps completed
        if self.percentage == 100 and not self.completed_at:
            self.completed_at = timezone.now()
        
        self.save()
