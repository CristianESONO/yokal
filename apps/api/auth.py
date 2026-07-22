import json
from functools import wraps

from django.http import JsonResponse
from django.utils import timezone

from apps.accounts.models import MerchantProfile


def _extract_api_key(request):
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth[7:].strip()
    return request.headers.get('X-API-Key', '').strip()


def api_key_required(view_func):
    """Authenticate merchant requests via API key."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        key = _extract_api_key(request)
        if not key:
            return JsonResponse(
                {'error': 'Clé API manquante. Utilisez Authorization: Bearer <clé> ou X-API-Key.'},
                status=401,
            )

        merchant = MerchantProfile.objects.filter(api_key=key, api_key_active=True).first()
        if not merchant:
            return JsonResponse({'error': 'Clé API invalide ou inactive.'}, status=401)

        MerchantProfile.objects.filter(pk=merchant.pk).update(api_key_last_used=timezone.now())
        request.merchant = merchant
        return view_func(request, *args, **kwargs)

    return wrapper


def json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
