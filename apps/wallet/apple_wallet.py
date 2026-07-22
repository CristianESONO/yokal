"""
Apple Wallet (PassKit) integration for loyalty cards.

References:
  https://developer.apple.com/documentation/walletpasses
  https://developer.apple.com/library/archive/documentation/PassKit/Conceptual/PassKit_PG/

Requires:
  - APPLE_PASS_TYPE_ID (Pass Type ID from Apple Developer)
  - APPLE_TEAM_ID (Team ID from Apple Developer)
  - APPLE_CERTIFICATE_PATH (Path to .p12 certificate)
  - APPLE_CERTIFICATE_PASSWORD (Password for .p12 certificate)
  - APPLE_WWDR_CERT_PATH (Path to Apple Worldwide Developer Relations CA)
"""

import os
import json
import zipfile
import tempfile
import hashlib
import logging
from datetime import datetime, timedelta

from django.conf import settings

logger = logging.getLogger(__name__)


def is_apple_wallet_configured():
    """Return True if Apple Wallet credentials are configured."""
    return all([
        getattr(settings, 'APPLE_PASS_TYPE_ID', None),
        getattr(settings, 'APPLE_TEAM_ID', None),
        getattr(settings, 'APPLE_CERTIFICATE_PATH', None),
        getattr(settings, 'APPLE_CERTIFICATE_PASSWORD', None),
    ])


def _get_pass_config():
    """Return Apple Wallet configuration or None if not configured."""
    if not is_apple_wallet_configured():
        return None
    
    return {
        'pass_type_id': settings.APPLE_PASS_TYPE_ID,
        'team_id': settings.APPLE_TEAM_ID,
        'cert_path': settings.APPLE_CERTIFICATE_PATH,
        'cert_password': settings.APPLE_CERTIFICATE_PASSWORD,
        'wwdr_cert_path': getattr(settings, 'APPLE_WWDR_CERT_PATH', None),
    }


def _generate_pass_json(card):
    """Generate the pass.json payload for a loyalty card."""
    program = card.program
    merchant = program.merchant
    
    # Calculate progress to reward
    progress = min(100, (float(card.balance) / float(program.reward_threshold)) * 100)
    
    pass_json = {
        "formatVersion": 1,
        "passTypeIdentifier": settings.APPLE_PASS_TYPE_ID,
        "serialNumber": f"yokal_card_{card.pk}",
        "teamIdentifier": settings.APPLE_TEAM_ID,
        "webServiceURL": settings.SITE_URL.rstrip('/'),
        "authenticationToken": str(card.qr_token),
        "description": f"Carte fidélité {program.name}",
        "organizationName": merchant.business_name,
        "logoText": merchant.business_name,
        "foregroundColor": "#ffffff",
        "backgroundColor": program.color_primary or "#111827",
        "labelColor": "#ffffff",
        "relevantDate": card.created_at.isoformat(),
        "expirationDate": (card.created_at + timedelta(days=365)).isoformat(),
        
        "generic": {
            "primaryFields": [
                {
                    "key": "balance",
                    "label": program.unit_label,
                    "value": str(int(card.balance))
                }
            ],
            "secondaryFields": [
                {
                    "key": "threshold",
                    "label": "Seuil",
                    "value": str(program.reward_threshold)
                },
                {
                    "key": "customer",
                    "label": "Client",
                    "value": card.customer_name
                }
            ],
            "auxiliaryFields": [
                {
                    "key": "program",
                    "label": "Programme",
                    "value": program.name
                },
                {
                    "key": "reward",
                    "label": "Récompense",
                    "value": program.reward_description
                }
            ],
            "backFields": [
                {
                    "key": "merchant",
                    "label": "Commerce",
                    "value": merchant.business_name
                },
                {
                    "key": "address",
                    "label": "Adresse",
                    "value": merchant.address or ""
                },
                {
                    "key": "phone",
                    "label": "Téléphone",
                    "value": merchant.phone or ""
                },
                {
                    "key": "terms",
                    "label": "Conditions",
                    "value": "Carte de fidélité Yokalma. Non transférable."
                }
            ]
        },
        
        "barcode": {
            "format": "PKBarcodeFormatQR",
            "message": str(card.qr_token),
            "messageEncoding": "iso-8859-1",
            "altText": str(card.qr_token)[:8].upper()
        }
    }
    
    return pass_json


def _create_pkpass_archive(pass_json, card):
    """
    Create a signed .pkpass archive.
    
    Returns the path to the temporary .pkpass file or None on error.
    """
    config = _get_pass_config()
    if not config:
        logger.error("Apple Wallet not configured")
        return None
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        pass_dir = os.path.join(temp_dir, 'pass')
        os.makedirs(pass_dir)
        
        # Write pass.json
        with open(os.path.join(pass_dir, 'pass.json'), 'w') as f:
            json.dump(pass_json, f)
        
        # Copy images if available
        if program.logo and hasattr(program.logo, 'path'):
            logo_path = program.logo.path
            if os.path.exists(logo_path):
                # Copy as icon
                import shutil
                shutil.copy(logo_path, os.path.join(pass_dir, 'icon.png'))
                shutil.copy(logo_path, os.path.join(pass_dir, 'logo.png'))
        
        # Create manifest
        manifest = {}
        for filename in os.listdir(pass_dir):
            filepath = os.path.join(pass_dir, filename)
            with open(filepath, 'rb') as f:
                file_hash = hashlib.sha1(f.read()).hexdigest()
            manifest[filename] = file_hash
        
        with open(os.path.join(pass_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest, f)
        
        # Sign the manifest
        signature = _sign_manifest(manifest, config)
        if not signature:
            return None
        
        with open(os.path.join(pass_dir, 'signature'), 'wb') as f:
            f.write(signature)
        
        # Create ZIP archive (.pkpass)
        pkpass_path = os.path.join(temp_dir, f'yokal_card_{card.pk}.pkpass')
        with zipfile.ZipFile(pkpass_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename in os.listdir(pass_dir):
                filepath = os.path.join(pass_dir, filename)
                zf.write(filepath, filename)
        
        return pkpass_path
        
    except Exception as e:
        logger.exception(f"Error creating pkpass archive: {e}")
        return None


def _sign_manifest(manifest, config):
    """
    Sign the manifest using Apple certificate.
    
    Returns the signature bytes or None on error.
    """
    try:
        from OpenSSL import crypto, SSL
        
        # Load certificate
        with open(config['cert_path'], 'rb') as f:
            cert_data = f.read()
        
        cert = crypto.load_certificate(crypto.FILETYPE_ASN1, cert_data)
        key = crypto.load_privatekey(crypto.FILETYPE_ASN1, cert_data, config['cert_password'].encode())
        
        # Load WWDR certificate if available
        wwdr_cert = None
        if config['wwdr_cert_path'] and os.path.exists(config['wwdr_cert_path']):
            with open(config['wwdr_cert_path'], 'rb') as f:
                wwdr_cert = crypto.load_certificate(crypto.FILETYPE_ASN1, f.read())
        
        # Create PKCS7 signature
        manifest_json = json.dumps(manifest).encode('utf-8')
        
        bio = crypto._new_mem_buf(manifest_json)
        pkcs7 = crypto.PKCS7(cert, key)
        
        if wwdr_cert:
            pkcs7.set_certificate(wwdr_cert)
        
        pkcs7.set_type(PKCS7.SIGNED)
        pkcs7.sign(bio, flags=crypto.PKCS7.DETACHED | crypto.PKCS7.BINARY)
        
        return crypto.dump_pkcs7(pkcs7)
        
    except ImportError:
        logger.error("pyOpenSSL not installed. Install with: pip install pyOpenSSL")
        return None
    except Exception as e:
        logger.exception(f"Error signing manifest: {e}")
        return None


def generate_apple_wallet_pass(card):
    """
    Generate an Apple Wallet pass (.pkpass) for a loyalty card.
    
    Returns the path to the .pkpass file or None on error.
    """
    if not is_apple_wallet_configured():
        logger.warning("Apple Wallet not configured")
        return None
    
    try:
        pass_json = _generate_pass_json(card)
        pkpass_path = _create_pkpass_archive(pass_json, card)
        
        if pkpass_path:
            logger.info(f"Generated Apple Wallet pass for card {card.pk}")
            return pkpass_path
        else:
            logger.error(f"Failed to generate Apple Wallet pass for card {card.pk}")
            return None
            
    except Exception as e:
        logger.exception(f"Error generating Apple Wallet pass: {e}")
        return None


def update_apple_wallet_pass(card):
    """
    Update an existing Apple Wallet pass.
    
    Note: Apple Wallet passes are updated via web service notifications.
    This function triggers a push notification to the device.
    """
    if not is_apple_wallet_configured():
        return False
    
    try:
        # In a full implementation, this would use Apple's PassKit Web Service
        # to send an update notification to devices that have the pass.
        # For now, we'll just log the update.
        logger.info(f"Apple Wallet pass update triggered for card {card.pk}")
        
        # TODO: Implement web service notification
        # Requires setting up a REST endpoint for Apple's update callbacks
        
        return True
        
    except Exception as e:
        logger.exception(f"Error updating Apple Wallet pass: {e}")
        return False


def get_apple_wallet_pass_url(card):
    """
    Generate a URL to download the .pkpass file.
    
    Returns the URL or None if not configured.
    """
    if not is_apple_wallet_configured():
        return None
    
    site_url = settings.SITE_URL.rstrip('/')
    return f"{site_url}/wallet/apple-pass/{card.pk}/"
