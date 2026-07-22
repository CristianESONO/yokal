from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import MerchantProfile
from apps.billing.services import ensure_merchant_subscription


@receiver(post_save, sender=MerchantProfile)
def create_merchant_subscription(sender, instance, created, **kwargs):
    if created:
        ensure_merchant_subscription(instance)
