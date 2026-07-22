"""
Google Wallet Loyalty API integration.

References:
  https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyclass
  https://developers.google.com/wallet/retail/loyalty-cards/rest/v1/loyaltyobject

Requires:
  - GOOGLE_WALLET_ISSUER_ID  (from Google Pay & Wallet Console)
  - GOOGLE_SERVICE_ACCOUNT_FILE  (path to service account JSON)
"""

import json
import uuid
import logging
import datetime

from django.conf import settings

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
        import requests
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


# ──────────────────────────────────────────────────────
#  LOYALTY CLASS  (one per LoyaltyProgram)
# ──────────────────────────────────────────────────────

def create_loyalty_class(program):
    """Create or update a Google Wallet LoyaltyClass for a program."""
    session = _get_session()
    if not session:
        return None

    class_id = _class_id(program)
    payload = {
        "id": class_id,
        "issuerName": program.merchant.business_name,
        "programName": program.name,
        "programLogo": {
            "sourceUri": {"uri": "https://storage.googleapis.com/wallet-lab-tools-codelab-artifacts-public/pass_google_logo.jpg"},
            "contentDescription": {"defaultValue": {"language": "fr-FR", "value": program.name}}
        },
        "rewardsTier": program.reward_description,
        "rewardsTierLabel": "Récompense",
        "loyaltyPoints": {
            "label": program.unit_label,
            "balance": {"int": {"value": 0}}
        },
        "hexBackgroundColor": program.color_primary,
        "reviewStatus": "UNDER_REVIEW",
    }

    # Check if class already exists
    check = session.get(f"{WALLET_API}/loyaltyClass/{class_id}")
    if check.status_code == 200:
        resp = session.put(f"{WALLET_API}/loyaltyClass/{class_id}", json=payload)
    else:
        resp = session.post(f"{WALLET_API}/loyaltyClass", json=payload)

    if resp.status_code in (200, 201):
        program.google_wallet_class_id = class_id
        program.save(update_fields=['google_wallet_class_id'])
        logger.info(f"LoyaltyClass {class_id} synced.")
    else:
        logger.error(f"LoyaltyClass error: {resp.status_code} {resp.text}")

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
            "balance": {"int": {"value": int(card.balance)}}
        },
        "secondaryLoyaltyPoints": {
            "label": "Récompense à",
            "balance": {"string": {"value": f"{program.reward_threshold} {program.unit_label}"}}
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

    check = session.get(f"{WALLET_API}/loyaltyObject/{object_id}")
    if check.status_code == 200:
        resp = session.put(f"{WALLET_API}/loyaltyObject/{object_id}", json=payload)
    else:
        resp = session.post(f"{WALLET_API}/loyaltyObject", json=payload)

    if resp.status_code in (200, 201):
        card.google_wallet_object_id = object_id
        card.google_wallet_linked = True
        card.save(update_fields=['google_wallet_object_id', 'google_wallet_linked'])
        logger.info(f"LoyaltyObject {object_id} created.")
    else:
        logger.error(f"LoyaltyObject error: {resp.status_code} {resp.text}")

    return object_id


def update_loyalty_object(card):
    """Update stamp count on an existing Google Wallet LoyaltyObject."""
    session = _get_session()
    if not session:
        return

    object_id = _object_id(card)
    patch = {
        "loyaltyPoints": {
            "label": card.program.unit_label,
            "balance": {"int": {"value": int(card.balance)}}
        }
    }
    resp = session.patch(f"{WALLET_API}/loyaltyObject/{object_id}", json=patch)
    if resp.status_code == 200:
        logger.info(f"LoyaltyObject {object_id} updated — {card.stamp_count} stamps.")
    else:
        logger.error(f"LoyaltyObject patch error: {resp.status_code} {resp.text}")


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
        return None  # Templates handle None gracefully

    try:
        import google.auth.crypt
        import google.auth.jwt

        with open(sa_file) as f:
            sa_info = json.load(f)

        object_id = _object_id(card)

        claims = {
            "iss": sa_info["client_email"],
            "aud": "google",
            "origins": ["*"],
            "typ": "savetowallet",
            "payload": {
                "loyaltyObjects": [{"id": object_id}]
            },
            "iat": int(datetime.datetime.utcnow().timestamp()),
        }

        signer = google.auth.crypt.RSASigner.from_service_account_info(sa_info)
        token = google.auth.jwt.encode(signer, claims).decode("utf-8")
        return f"https://pay.google.com/gp/v/save/{token}"
    except Exception as e:
        logger.error(f"generate_add_to_wallet_url error: {e}")
        return None
