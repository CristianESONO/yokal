"""
Apple Wallet (PassKit) views for serving .pkpass files.
"""

import os
import logging
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

from apps.loyalty.models import LoyaltyCard
from apps.wallet.apple_wallet import (
    generate_apple_wallet_pass,
    is_apple_wallet_configured,
)

logger = logging.getLogger(__name__)


@require_GET
def download_apple_pass(request, card_id):
    """
    Download a .pkpass file for a loyalty card.
    
    This endpoint is public (no authentication required) because the customer
    needs to be able to download the pass from their phone.
    """
    card = get_object_or_404(LoyaltyCard, pk=card_id, is_deleted=False)
    
    if not is_apple_wallet_configured():
        return HttpResponse(
            "<h2>Apple Wallet non configuré</h2>"
            "<p>La fonctionnalité Apple Wallet n'est pas disponible.</p>",
            status=503,
        )
    
    try:
        pkpass_path = generate_apple_wallet_pass(card)
        
        if not pkpass_path:
            return HttpResponse(
                "<h2>Erreur de génération</h2>"
                "<p>Impossible de générer le pass Apple Wallet.</p>",
                status=500,
            )
        
        # Serve the .pkpass file
        response = FileResponse(
            open(pkpass_path, 'rb'),
            content_type='application/vnd.apple.pkpass'
        )
        response['Content-Disposition'] = f'attachment; filename="yokal_card_{card_id}.pkpass"'
        
        # Clean up temporary file after sending
        import atexit
        atexit.register(lambda: os.unlink(pkpass_path) if os.path.exists(pkpass_path) else None)
        
        return response
        
    except Exception as e:
        logger.exception(f"Error serving Apple Wallet pass for card {card_id}: {e}")
        return HttpResponse(
            "<h2>Erreur serveur</h2>"
            "<p>Une erreur est survenue lors du téléchargement du pass.</p>",
            status=500,
        )


@login_required
def apple_wallet_settings(request):
    """
    View for configuring Apple Wallet settings (admin only).
    """
    from django.contrib.auth.decorators import user_passes_test
    
    if not request.user.is_staff:
        return HttpResponse("Accès non autorisé", status=403)
    
    if request.method == 'POST':
        # Update Apple Wallet settings
        from django.conf import settings
        from django.core.files.storage import default_storage
        
        # Handle certificate upload
        cert_file = request.FILES.get('apple_certificate')
        if cert_file:
            cert_path = default_storage.save('wallet/apple_cert.p12', cert_file)
            # Store in settings or database
        
        # TODO: Implement proper settings storage
        pass
    
    context = {
        'is_configured': is_apple_wallet_configured(),
        'pass_type_id': getattr(settings, 'APPLE_PASS_TYPE_ID', None),
        'team_id': getattr(settings, 'APPLE_TEAM_ID', None),
    }
    
    return HttpResponse(
        f"<h2>Configuration Apple Wallet</h2>"
        f"<p>Configuré: {'Oui' if context['is_configured'] else 'Non'}</p>"
        f"<p>Pass Type ID: {context['pass_type_id'] or 'Non défini'}</p>"
        f"<p>Team ID: {context['team_id'] or 'Non défini'}</p>"
    )
