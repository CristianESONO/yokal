from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse


def subscription_required(view_func):
    """
    Décorateur qui vérifie si l'abonnement du marchand est valide.
    Si l'abonnement est expiré, redirige vers la page de facturation.
    Pour les requêtes AJAX, renvoie une erreur JSON 403.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from apps.accounts.utils import get_merchant
        from apps.billing.services import ensure_merchant_subscription
        
        merchant = get_merchant(request.user)
        if not merchant:
            messages.error(request, "Commerce non configuré.")
            return redirect('loyalty:landing')
        
        # TEMPORAIREMENT DÉSACTIVÉ - Vérification abonnement expiré désactivée
        sub = ensure_merchant_subscription(merchant)
        # if sub and not sub.is_compliant:
        #     # Check if it's an AJAX request
        #     if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        #         return JsonResponse({
        #             'error': "Abonnement expiré. Veuillez renouveler pour continuer.",
        #             'redirect_url': '/dashboard/billing/'
        #         }, status=403)
        #     
        #     messages.error(
        #         request,
        #         "⚠️ Votre abonnement a expiré. Veuillez le renouveler pour continuer."
        #     )
        #     return redirect('dashboard:billing')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def subscription_read_only(view_func):
    """
    Décorateur qui permet l'accès en lecture seule si l'abonnement est expiré.
    Les données sont visibles mais les actions d'écriture sont bloquées.
    Ajoute un contexte 'read_only_mode' au template.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from apps.accounts.utils import get_merchant
        from apps.billing.services import ensure_merchant_subscription
        
        merchant = get_merchant(request.user)
        read_only_mode = False
        
        if merchant:
            sub = ensure_merchant_subscription(merchant)
            if sub and not sub.is_compliant:
                read_only_mode = True
        
        # Add read_only_mode to the view's context
        response = view_func(request, *args, **kwargs)
        
        if hasattr(response, 'context_data'):
            response.context_data['read_only_mode'] = read_only_mode
        elif hasattr(response, 'context'):
            response.context['read_only_mode'] = read_only_mode
        
        return response
    return _wrapped_view
