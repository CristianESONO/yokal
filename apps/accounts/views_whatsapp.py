import json
import logging
import requests

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.loyalty.whatsapp_service import WhatsAppService
from apps.accounts.utils import get_merchant

logger = logging.getLogger(__name__)

@login_required
@require_POST
def connect_whatsapp(request):
    try:
        merchant = get_merchant(request.user)
        if not merchant:
            return JsonResponse({'error': 'Non autorisé'}, status=403)

        instance_name = f"yokal_m{merchant.id}"

        # Delete existing instance to avoid naming conflicts on reset
        try:
            WhatsAppService.delete_instance(instance_name, merchant=merchant)
        except:
            pass

        # Create the instance
        # Now raises exceptions instead of returning None
        WhatsAppService.create_instance(instance_name, merchant=merchant)

        # Save state
        merchant.whatsapp_instance_id = instance_name
        merchant.whatsapp_instance_name = instance_name
        merchant.whatsapp_connected = False
        merchant.save(update_fields=['whatsapp_instance_id', 'whatsapp_instance_name', 'whatsapp_connected'])

        # Try to get QR code
        qr = WhatsAppService.get_qrcode(instance_name, merchant=merchant)

        return JsonResponse({
            'success': True,
            'instance_name': instance_name,
            'qrcode': qr,
        })
    except Exception as e:
        logger.exception(f"Error in connect_whatsapp: {e}")
        return JsonResponse({'error': f"Erreur Diagnostic (QR): {str(e)}"}, status=500)


@login_required
@require_POST
def whatsapp_pairing_code(request):
    try:
        merchant = get_merchant(request.user)
        if not merchant or not merchant.phone:
            return JsonResponse({'error': 'Veuillez renseigner votre téléphone dans votre profil.'}, status=400)
        
        import time
        phone = "".join(filter(str.isdigit, str(merchant.phone)))
        
        # Delete old instance (any previous name) to clean up
        old_instance = merchant.whatsapp_instance_id
        if old_instance:
            try:
                WhatsAppService.delete_instance(old_instance, merchant=merchant)
            except:
                pass

        # Use a fresh unique name to avoid WhatsApp server-side caching of the session
        ts = int(time.time())
        instance_name = f"yokal_m{merchant.id}_{ts}"
        
        # CRITICAL: qrcode=False so Baileys starts in pairing code mode, not QR mode
        WhatsAppService.create_instance(instance_name, merchant=merchant, qrcode=False)
        
        # Save instance reference
        merchant.whatsapp_instance_id = instance_name
        merchant.whatsapp_instance_name = instance_name
        merchant.whatsapp_connected = False
        merchant.save(update_fields=['whatsapp_instance_id', 'whatsapp_instance_name', 'whatsapp_connected'])

        # Wait for the instance to fully initialize
        time.sleep(5)

        # Retry up to 4 times with 3-second intervals
        code = None
        for attempt in range(4):
            try:
                code = WhatsAppService.get_pairing_code(instance_name, phone, merchant=merchant)
                if code:
                    break
            except Exception as e:
                logger.warning(f"[WhatsApp] Pairing attempt {attempt+1} failed: {e}")
            time.sleep(3)

        if not code:
            return JsonResponse({'error': "Code d'appairage non généré. Réessayez."}, status=500)

        return JsonResponse({'success': True, 'pairing_code': code, 'phone': phone})
    except Exception as e:
        logger.exception(f"Error in whatsapp_pairing_code: {e}")
        return JsonResponse({'error': f"Erreur Diagnostic (Pairing): {str(e)}"}, status=500)


@login_required
def whatsapp_qrcode(request):
    try:
        merchant = get_merchant(request.user)
        if not merchant or not merchant.whatsapp_instance_id:
            return JsonResponse({'error': 'Instance non trouvée'}, status=400)
        qr = WhatsAppService.get_qrcode(merchant.whatsapp_instance_id, merchant=merchant)
        return JsonResponse({'qrcode': qr})
    except Exception as e:
        return JsonResponse({'error': f"Erreur Diagnostic (QR Fetch): {str(e)}"}, status=500)


@login_required
def whatsapp_status(request):
    try:
        merchant = get_merchant(request.user)
        if not merchant or not merchant.whatsapp_instance_id:
            return JsonResponse({'connected': False, 'state': None})

        state = WhatsAppService.check_connection(merchant.whatsapp_instance_id, merchant=merchant)
        is_connected = (state == 'open' or state == 'CONNECTED')

        if is_connected != merchant.whatsapp_connected:
            merchant.whatsapp_connected = is_connected
            if is_connected:
                merchant.whatsapp_last_seen = timezone.now()
                merchant.whatsapp_enabled = True
            merchant.save(update_fields=['whatsapp_connected', 'whatsapp_last_seen', 'whatsapp_enabled'])

        return JsonResponse({
            'state': state,
            'connected': is_connected,
            'last_seen': merchant.whatsapp_last_seen.strftime('%d/%m/%Y %H:%M') if merchant.whatsapp_last_seen else None,
        })
    except Exception as e:
        return JsonResponse({'error': f"Erreur Diagnostic (Status): {str(e)}"}, status=500)


@login_required
@require_POST
def disconnect_whatsapp(request):
    try:
        merchant = get_merchant(request.user)
        if merchant.whatsapp_instance_id:
            try:
                WhatsAppService.delete_instance(merchant.whatsapp_instance_id, merchant=merchant)
            except:
                pass
        
        merchant.whatsapp_instance_id = None
        merchant.whatsapp_instance_name = None
        merchant.whatsapp_connected = False
        merchant.whatsapp_enabled = False
        merchant.save(update_fields=['whatsapp_instance_id', 'whatsapp_instance_name', 'whatsapp_connected', 'whatsapp_enabled'])
        messages.success(request, "WhatsApp déconnecté.")
    except Exception as e:
        messages.error(request, f"Erreur de déconnexion: {str(e)}")
    return redirect('dashboard:settings')


@login_required
@require_POST
def update_whatsapp_settings(request):
    try:
        merchant = get_merchant(request.user)
        url = request.POST.get('whatsapp_api_url', '').strip()
        key = request.POST.get('whatsapp_api_key', '').strip()

        merchant.whatsapp_api_url = url
        merchant.whatsapp_api_key = key
        merchant.save(update_fields=['whatsapp_api_url', 'whatsapp_api_key'])

        messages.success(request, "Paramètres WhatsApp enregistrés.")
    except Exception as e:
        messages.error(request, f"Erreur de sauvegarde: {str(e)}")
    return redirect('dashboard:settings')


@login_required
@require_POST
def toggle_whatsapp_notifications(request):
    merchant = get_merchant(request.user)
    enabled = request.POST.get('whatsapp_enabled') == '1'
    if enabled and not merchant.whatsapp_connected:
        return JsonResponse({'error': 'WhatsApp non connecté.'}, status=400)
    merchant.whatsapp_enabled = enabled
    merchant.save(update_fields=['whatsapp_enabled'])
    return JsonResponse({'success': True})


@login_required
@require_POST
def bulk_whatsapp_notification(request):
    try:
        merchant = get_merchant(request.user)
        if not merchant or not merchant.whatsapp_connected:
            return JsonResponse({'error': 'Connectez WhatsApp d\'abord.'}, status=400)

        # Vérifier si le plan inclut WhatsApp illimité
        from apps.billing.services import ensure_merchant_subscription
        sub = ensure_merchant_subscription(merchant)
        if sub and not sub.plan.includes_whatsapp_unlimited:
            return JsonResponse({'error': 'Votre plan n\'inclut pas les campagnes WhatsApp illimitées.'}, status=403)

        notify_type = request.POST.get('type')
        message_template = request.POST.get('message')

        if not message_template:
            return JsonResponse({'error': 'Le message est requis.'}, status=400)

        from apps.dashboard.utils import get_current_program
        program, _ = get_current_program(request, merchant)
        
        if not program:
            return JsonResponse({'error': 'Aucun programme de fidélité trouvé.'}, status=400)
        
        cards = program.cards.filter(is_deleted=False).exclude(customer_phone='')

        if notify_type == 'rewards':
            cards = cards.filter(rewards__redeemed=False).distinct()
        elif notify_type == 'close':
            min_balance = float(program.reward_threshold) * 0.7
            cards = cards.filter(balance__gte=min_balance)

        sent = 0
        failed = 0
        total_cards = cards.count()
        
        for card in cards:
            try:
                msg = message_template.replace('{nom}', card.customer_name).replace('{points}', str(int(card.balance)))
                if WhatsAppService.send_text_message(merchant.whatsapp_instance_id, card.customer_phone, msg, merchant=merchant):
                    sent += 1
                else:
                    failed += 1
                import time
                time.sleep(0.5)  # Réduit à 0.5s pour éviter les timeouts
            except Exception as e:
                logger.warning(f"Failed to send WhatsApp to {card.customer_phone}: {e}")
                failed += 1
            
        return JsonResponse({
            'success': True, 
            'sent': sent, 
            'failed': failed, 
            'total': total_cards
        })
    except Exception as e:
        logger.exception(f"Error in bulk_whatsapp_notification: {e}")
        return JsonResponse({'error': str(e)}, status=500)
