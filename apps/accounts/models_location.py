"""
Location model for multi-point of sale support.
Allows a single merchant to manage multiple locations.
"""

from django.db import models
from django.utils.text import slugify


class Location(models.Model):
    """Physical location/store for a merchant."""
    merchant = models.ForeignKey(
        'MerchantProfile',
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name="Marchand"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nom du point de vente"
    )
    address = models.TextField(
        blank=True,
        verbose_name="Adresse"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ville"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Email"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="Siège principal"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="Slug"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Point de vente"
        verbose_name_plural = "Points de vente"
        ordering = ['-is_main', 'name']

    def __str__(self):
        return f"{self.name} - {self.merchant.business_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.merchant.business_name}-{self.name}")
            self.slug = base_slug
            counter = 1
            while Location.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        # Ensure only one main location
        if self.is_main:
            Location.objects.filter(
                merchant=self.merchant,
                is_main=True
            ).exclude(pk=self.pk).update(is_main=False)
        
        super().save(*args, **kwargs)
