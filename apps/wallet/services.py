"""
Google Wallet Loyalty API integration.

References:
  https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass
  https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject

Requires:
  - GOOGLE_WALLET_ISSUER_ID  (from Google Pay & Wallet Console)
  - GOOGLE_SERVICE_ACCOUNT_FILE  (path to service account JSON)
Optional:
  - DEFAULT_WALLET_LOGO_URL (public URL to fallback logo)
"""

import json
import uuid
import logging
import datetime

from django.conf import settings

import requests  # used for image validation and optional direct calls

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/wallet_object.issuer']
WALLET_API = 'https://walletobjects.googleapis.com/walletobjects/v1'


def _get_credentials():
    """Return Google service account credentials, or None if not configured."""
    sa_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
    if not sa_file:
        logger.warning("Google Wallet: GOOGLE_SERVICE_ACCOUNT_FILE not set — skipping API calls.")
        return None
    try:
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(
            sa_file, scopes=SCOPES
        )
        return credentials
    except Exception as e:
        logger.error(f"Google Wallet credentials error: {e}")
        return None


def _get_session():
    """Return an authorized requests.Session or None."""
    credentials = _get_credentials()
    if not credentials:
        return None
    try:
        import google.auth.transport.requests
        credentials.refresh(google.auth.transport.requests.Request())
        session = requests.Session()
        session.headers.update({'Authorization': f'Bearer {credentials.token}'})
        return session
    except Exception as e:
        logger.error(f"Google Wallet session error: {e}")
        return None


def _class_id(program):
    """Return the Google Wallet class ID for a program."""
    issuer_id = settings.GOOGLE_WALLET_ISSUER_ID
    return f"{issuer_id}.yokal_program_{program.pk}"


def _object_id(card):
    """Return the Google Wallet object ID for a card."""
    issuer_id = settings.GOOGLE_WALLET_ISSUER_ID
    return f"{issuer_id}.yokal_card_{card.pk}"


def _absolute_url(path_or_url):
    """Return an absolute public URL for Google Wallet image validation."""
    if not path_or_url:
        return None
    if path_or_url.startswith(('http://', 'https://')):
        return path_or_url
    site = settings.SITE_URL.rstrip('/')
    if not path_or_url.startswith('/'):
        path_or_url = f'/{path_or_url}'
    return f'{site}{path_or_url}'


def is_wallet_configured():
    """Return True if Google Wallet credentials are configured."""
    return bool(settings.GOOGLE_SERVICE_ACCOUNT_FILE and settings.GOOGLE_WALLET_ISSUER_ID)


def _is_public_image(url, timeout=5):
    """Return True if URL responds 200 and content-type is image/*."""
    if not url:
        return False
    try:
        r = requests.head(url, allow_redirects=True, timeout=timeout)
        ct = r.headers.get('content-type', '')
        return r.status_code == 200 and ct.startswith('image/')
    except Exception:
        return False


# ──────────────────────────────────────────────────────
#  LOYALTY CLASS  (one per LoyaltyProgram)
# ──────────────────────────────────────────────────────

def create_loyalty_class(program):
    """Create or update a Google Wallet LoyaltyClass for a program."""
    session = _get_session()
    if not session:
        return None

    class_id = _class_id(program)

    # Determine candidate logos: program.logo, settings.DEFAULT_WALLET_LOGO_URL
    logo_uri = None
    try:
        candidates = []
        if getattr(program, "logo", None) and getattr(program.logo, "url", None):
            candidates.append(_absolute_url(program.logo.url))
        default_logo = getattr(settings, "DEFAULT_WALLET_LOGO_URL", None)
        if default_logo:
            candidates.append(_absolute_url(default_logo))

        for cand in candidates:
            if _is_public_image(cand):
                logo_uri = cand
                break

        if not logo_uri:
            # Google requires a programLogo for LoyaltyClass creation.
            logger.error(
                "No public logo found for program %s (candidates: %s). Skipping class creation to avoid API 400.",
                program.pk, candidates
            )
            return class_id
    except Exception:
        logo_uri = None
        logger.exception("Error while resolving logo for program %s", program.pk)
        return class_id

    payload = {
        "id": class_id,
        "issuerName": program.merchant.business_name,
        "programName": program.name,
        "rewardsTier": program.reward_description,
        "rewardsTierLabel": "Récompense",
        "loyaltyPoints": {
            "label": program.unit_label,
            "balance": {"int": 0},
        },
        "hexBackgroundColor": program.color_primary or "#111827",
        "reviewStatus": "ACTIVE",
        "programLogo": {
            "sourceUri": {"uri": logo_uri},
            "contentDescription": {"defaultValue": {"language": "fr-FR", "value": program.name}}
        }
    }

    # Check if class already exists
    try:
        check = session.get(f"{WALLET_API}/loyaltyClass/{class_id}")
    except Exception as e:
        logger.exception("HTTP error when checking LoyaltyClass %s: %s", class_id, e)
        return class_id

    try:
        if check.status_code == 200:
            resp = session.put(f"{WALLET_API}/loyaltyClass/{class_id}", json=payload, timeout=30)
        else:
            resp = session.post(f"{WALLET_API}/loyaltyClass", json=payload, timeout=30)
    except Exception as e:
        logger.exception("HTTP error when syncing LoyaltyClass %s: %s", class_id, e)
        return class_id

    logger.debug("LoyaltyClass payload: %s", payload)
    logger.debug("LoyaltyClass response: %s %s", resp.status_code, resp.text)

    if resp.status_code in (200, 201):
        try:
            program.google_wallet_class_id = class_id
            program.save(update_fields=["google_wallet_class_id"])
        except Exception:
            logger.exception("Failed saving google_wallet_class_id on program %s", program.pk)
        logger.info("LoyaltyClass %s synced.", class_id)
    else:
        logger.error("LoyaltyClass error: %s %s", resp.status_code, resp.text)

    return class_id


# ──────────────────────────────────────────────────────
#  LOYALTY OBJECT  (one per LoyaltyCard / customer)
# ──────────────────────────────────────────────────────

def create_loyalty_object(card):
    """Create a Google Wallet LoyaltyObject for a customer card."""
    session = _get_session()
    if not session:
        return None

    program = card.program
    if not program.google_wallet_class_id:
        create_loyalty_class(program)

    object_id = _object_id(card)
    payload = {
        "id": object_id,
        "classId": _class_id(program),
        "state": "ACTIVE",
        "accountId": str(card.qr_token),
        "accountName": card.customer_name,
        "loyaltyPoints": {
            "label": program.unit_label,
            "balance": {"int": int(card.balance)},
        },
        "secondaryLoyaltyPoints": {
            "label": "Seuil",
            "balance": {"string": str(program.reward_threshold)},
        },
        "barcode": {
            "type": "QR_CODE",
            "value": str(card.qr_token),
            "alternateText": str(card.qr_token)[:8].upper()
        },
        "textModulesData": [
            {
                "header": "Programme",
                "body": program.name,
                "id": "program_name"
            },
            {
                "header": "Récompense",
                "body": program.reward_description,
                "id": "reward_desc"
            }
        ],
    }

    try:
        check = session.get(f"{WALLET_API}/loyaltyObject/{object_id}")
    except Exception as e:
        logger.exception("HTTP error when checking LoyaltyObject %s: %s", object_id, e)
        return False

    try:
        if check.status_code == 200:
            resp = session.put(f"{WALLET_API}/loyaltyObject/{object_id}", json=payload, timeout=30)
        else:
            resp = session.post(f"{WALLET_API}/loyaltyObject", json=payload, timeout=30)
    except Exception as e:
        logger.exception("HTTP error when syncing LoyaltyObject %s: %s", object_id, e)
        return False

    if resp.status_code in (200, 201):
        try:
            card.google_wallet_object_id = object_id
            card.save(update_fields=['google_wallet_object_id'])
        except Exception:
            logger.exception("Failed saving google wallet fields for card %s", card.pk)
        logger.info("LoyaltyObject %s created.", object_id)
        return True

    logger.error("LoyaltyObject error: %s %s", resp.status_code, resp.text)
    return False


def update_loyalty_object(card):
    """Update stamp count on an existing Google Wallet LoyaltyObject."""
    session = _get_session()
    if not session:
        return

    object_id = _object_id(card)
    patch = {
        "loyaltyPoints": {
            "label": card.program.unit_label,
            "balance": {"int": int(card.balance)},
        }
    }
    try:
        resp = session.patch(f"{WALLET_API}/loyaltyObject/{object_id}", json=patch, timeout=20)
        if resp.status_code == 200:
            logger.info(f"LoyaltyObject {object_id} updated — {card.stamp_count} stamps.")
        else:
            logger.error(f"LoyaltyObject patch error: {resp.status_code} {resp.text}")
    except Exception as e:
        logger.exception("HTTP error when patching LoyaltyObject %s: %s", object_id, e)


# ──────────────────────────────────────────────────────
#  ADD-TO-WALLET SIGNED JWT LINK
# ──────────────────────────────────────────────────────

def generate_add_to_wallet_url(card):
    """
    Generate a signed JWT URL that the customer clicks to add the card
    to Google Wallet.

    Returns None if credentials are not configured (dev mode).
    """
    sa_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
    issuer_id = settings.GOOGLE_WALLET_ISSUER_ID

    if not sa_file or not issuer_id:
        logger.info("Google Wallet not configured — returning demo URL.")
        return None

    try:
        import google.auth.crypt
        import google.auth.jwt

        with open(sa_file) as f:
            sa_info = json.load(f)

        object_id = _object_id(card)
        site_url = settings.SITE_URL.rstrip('/')

        claims = {
            "iss": sa_info["client_email"],
            "aud": "google",
            "origins": [site_url],
            "typ": "savetowallet",
            "payload": {
                "loyaltyObjects": [{"id": object_id}]
            },
            "iat": int(datetime.datetime.utcnow().timestamp()),
        }

        signer = google.auth.crypt.RSASigner.from_service_account_info(sa_info)
        token = google.auth.jwt.encode(signer, claims)
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return f"https://pay.google.com/gp/v/save/{token}"
    except Exception as e:
        logger.error(f"generate_add_to_wallet_url error: {e}")
        return None