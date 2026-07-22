from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from loyalty.models import LoyaltyCard
from wallet.services import generate_add_to_wallet_url


def add_to_wallet(request, token):
    """Redirect customer to the Google Wallet 'Add' URL for their card."""
    card = get_object_or_404(LoyaltyCard, qr_token=token)
    url = generate_add_to_wallet_url(card)
    if url:
        return redirect(url)
    return HttpResponse(
        "<h2>Google Wallet non configuré pour le moment.</h2>"
        "<p>Contactez le commerçant.</p>",
        status=200
    )
