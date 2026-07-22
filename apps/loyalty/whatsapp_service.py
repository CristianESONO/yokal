import requests
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Service for interacting with the Evolution API (WhatsApp Gateway).
    The API URL and global key are configured in settings (from .env).
    Each merchant has their own instance identified by whatsapp_instance_id.
    """

    @classmethod
    def _base_url(cls, merchant=None):
        if merchant and merchant.whatsapp_api_url:
            return merchant.whatsapp_api_url.rstrip('/')
        return settings.EVOLUTION_API_URL.rstrip('/')

    @classmethod
    def _headers(cls, merchant=None):
        key = merchant.whatsapp_api_key if merchant and merchant.whatsapp_api_key else settings.EVOLUTION_API_KEY
        return {
            "apikey": key,
            "Content-Type": "application/json",
        }

    @classmethod
    def create_instance(cls, instance_name, merchant=None, qrcode=True):
        """
        Create a new Evolution API instance for a merchant.
        Use qrcode=False for pairing code mode (Baileys cannot switch modes after creation).
        If the instance already exists (403/409), treats it as success.
        """
        url = f"{cls._base_url(merchant)}/instance/create"
        payload = {
            "instanceName": instance_name,
            "qrcode": qrcode,
            "integration": "WHATSAPP-BAILEYS",
        }
        response = requests.post(url, json=payload, headers=cls._headers(merchant), timeout=15)
        # 403 or 409 usually means the instance already exists — that's acceptable
        if response.status_code in (403, 409):
            logger.info(f"[WhatsApp] Instance {instance_name} already exists (HTTP {response.status_code}), reusing.")
            return {'instanceName': instance_name, 'already_exists': True}
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_qrcode(cls, instance_name, merchant=None):
        """
        Get QR code base64 string to connect a WhatsApp account.
        Returns the base64 string.
        """
        url = f"{cls._base_url(merchant)}/instance/connect/{instance_name}"
        response = requests.get(url, headers=cls._headers(merchant), timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get('base64') or data.get('code')

    @classmethod
    def get_pairing_code(cls, instance_name, phone, merchant=None):
        """
        Get a pairing code for mobile connection.
        Official Evolution API v2 method: GET /instance/connect/{name}?number={phone}
        """
        base = cls._base_url(merchant)
        headers = cls._headers(merchant)
        
        # Ensure number is digits only
        phone_clean = "".join(filter(str.isdigit, str(phone)))
        # IMPORTANT: &save=true is mandatory in this Evolution API version to trigger pairingCode
        url = f"{base}/instance/connect/{instance_name}?number={phone_clean}&save=true"

        last_error = None
        for attempt in range(2):
            try:
                import time
                if attempt > 0: time.sleep(2)
                
                logger.info(f"[WhatsApp] Requesting pairing code (attempt {attempt+1}): {url}")
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                
                # Only accept pairingCode (8-char). 'code' is the QR data, NOT the pairing code.
                code = data.get('pairingCode')
                if code and len(str(code)) <= 10:
                    return code
                
                last_error = f"pairingCode null ou absent. Réponse: {list(data.keys())}"
            except Exception as e:
                last_error = str(e)
                continue

        raise Exception(f"Code d'appairage non disponible. Détail: {last_error}")

    @classmethod
    def check_connection(cls, instance_name, merchant=None):
        """
        Check the connection state of an instance.
        """
        url = f"{cls._base_url(merchant)}/instance/connectionState/{instance_name}"
        response = requests.get(url, headers=cls._headers(merchant), timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('instance', {}).get('state') or data.get('state')

    @classmethod
    def delete_instance(cls, instance_name, merchant=None):
        """
        Delete/disconnect an Evolution API instance.
        """
        url = f"{cls._base_url(merchant)}/instance/delete/{instance_name}"
        response = requests.delete(url, headers=cls._headers(merchant), timeout=10)
        response.raise_for_status()
        return True

    @classmethod
    def send_message(cls, instance_name, number, text, merchant=None):
        """
        Send a WhatsApp text message through a merchant's instance.
        number should be in international format without '+' (e.g. 221770000000).
        Returns True on success, False otherwise.
        """
        # Clean the number
        phone = "".join(filter(str.isdigit, str(number)))
        if not phone:
            logger.warning(f"[WhatsApp] Empty phone number, skipping send.")
            return False

        try:
            url = f"{cls._base_url()}/message/sendText/{instance_name}"
            payload = {"number": phone, "text": text}
            response = requests.post(url, json=payload, headers=cls._headers(), timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"[WhatsApp] send_message failed for {instance_name} → {phone}: {e}")
            return False


# ─────────────────────────────────────────────
#  High-level helper: stamp notification
# ─────────────────────────────────────────────

def send_whatsapp_stamp_notification(card, amount_added):
    """
    Sends a WhatsApp notification to the customer after a stamp is added.
    Uses the merchant's own Evolution API instance.
    """
    merchant = card.program.merchant

    if not merchant.whatsapp_enabled:
        return False

    if not merchant.whatsapp_connected:
        logger.info(f"[WhatsApp] Merchant {merchant.business_name} not connected, skipping.")
        return False

    if not merchant.whatsapp_instance_id:
        logger.warning(f"[WhatsApp] No instance_id for merchant {merchant.business_name}")
        return False

    if not card.customer_phone:
        logger.warning(f"[WhatsApp] No phone for customer {card.customer_name}")
        return False

    # Build message
    program_name = card.program.name
    remaining = int(card.remaining_to_reward)
    unit = card.program.unit_label

    message = (
        f"Salut *{card.customer_name}*! 👋\n\n"
        f"Un nouveau tampon a été ajouté chez *{program_name}*! 💳\n"
        f"Contenu : +{int(amount_added)} {unit}\n"
    )

    if card.is_reward_ready:
        message += (
            f"\n🎉 *Félicitations !* Vous avez débloqué une récompense : "
            f"_{card.program.reward_description}_ ! "
            f"Présentez votre carte pour en profiter."
        )
    else:
        message += (
            f"\nIl vous reste encore *{remaining}* {unit} avant votre prochaine récompense : "
            f"_{card.program.reward_description}_. 🎁"
        )

    message += "\n\nMerci de votre fidélité ! ✨"

    # Update last seen timestamp
    merchant.whatsapp_last_seen = timezone.now()
    merchant.save(update_fields=['whatsapp_last_seen'])

    return WhatsAppService.send_message(
        merchant.whatsapp_instance_id,
        card.customer_phone,
        message,
    )
