from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from apps.loyalty.models import LoyaltyCard
from apps.wallet.services import create_loyalty_class, create_loyalty_object, generate_add_to_wallet_url


def add_to_wallet(request, token):
    """Redirect customer to the Google Wallet 'Add' URL for their card."""
    card = get_object_or_404(LoyaltyCard, qr_token=token)
    if not card.is_membership_usable:
        return HttpResponse(
            "<h2>Carte non disponible</h2>"
            "<p>Votre adhésion doit être validée par le commerçant avant d'ajouter la carte au wallet.</p>",
            status=403,
        )
    create_loyalty_class(card.program)
    if not create_loyalty_object(card):
        return HttpResponse(
            "<h2>Impossible d'ajouter la carte à Google Wallet pour le moment.</h2>"
            "<p>Veuillez réessayer dans quelques instants ou contactez le commerçant.</p>",
            status=503,
        )
    url = generate_add_to_wallet_url(card)
    if url:
        return redirect(url)
    return HttpResponse(
        "<h2>Google Wallet non configuré pour le moment.</h2>"
        "<p>Contactez le commerçant.</p>",
        status=200,
    )
