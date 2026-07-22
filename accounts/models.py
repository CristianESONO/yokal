from django.db import models
from django.contrib.auth.models import User


class MerchantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant_profile')
    business_name = models.CharField(max_length=150, verbose_name="Nom du commerce")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    country = models.CharField(max_length=100, default="Sénégal", verbose_name="Pays")
    logo = models.ImageField(upload_to='merchants/logos/', blank=True, null=True, verbose_name="Logo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil Marchand"

    def __str__(self):
        return self.business_name
