import hashlib
import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class PaytechError(Exception):
    pass


class PaytechService:
    @staticmethod
    def _headers():
        return {
            'API_KEY': settings.PAYTECH_API_KEY,
            'API_SECRET': settings.PAYTECH_API_SECRET,
            'Content-Type': 'application/json',
        }

    @staticmethod
    def is_configured():
        return bool(settings.PAYTECH_API_KEY and settings.PAYTECH_API_SECRET)

    @staticmethod
    def request_payment(*, item_name, item_price, ref_command, command_name,
                        custom_field, success_url, cancel_url, ipn_url,
                        payment_method='Orange Money, Wave, Free Money'):
        if not PaytechService.is_configured():
            return {'success': 0, 'message': 'PayTech non configuré sur le serveur.'}

        payload = {
            'item_name': item_name,
            'item_price': int(item_price),
            'currency': 'XOF',
            'ref_command': ref_command,
            'command_name': command_name,
            'env': settings.PAYTECH_ENV,
            'target_payment': payment_method,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'ipn_url': ipn_url,
            'custom_field': json.dumps(custom_field),
        }

        try:
            response = requests.post(
                f'{settings.PAYTECH_BASE_URL}/payment/request-payment',
                json=payload,
                headers=PaytechService._headers(),
                timeout=30,
            )
            data = response.json()
            if data.get('success') == 1:
                return data
            logger.error('PayTech error: %s', data)
            return data
        except requests.RequestException as exc:
            logger.exception('PayTech request failed')
            return {'success': 0, 'message': str(exc)}

    @staticmethod
    def verify_ipn(post_data):
        if not PaytechService.is_configured():
            return False

        api_key_sha256 = post_data.get('api_key_sha256', '')
        api_secret_sha256 = post_data.get('api_secret_sha256', '')

        expected_key = hashlib.sha256(settings.PAYTECH_API_KEY.encode()).hexdigest()
        expected_secret = hashlib.sha256(settings.PAYTECH_API_SECRET.encode()).hexdigest()

        return expected_key == api_key_sha256 and expected_secret == api_secret_sha256
