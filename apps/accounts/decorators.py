from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from apps.accounts.utils import get_team_role


def merchant_owner_required(view_func):
    """Restreint l'accès au propriétaire du commerce uniquement"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        role = get_team_role(request.user)
        if role != 'owner':
            messages.error(request, "Accès réservé au propriétaire du commerce.")
            return redirect('dashboard:overview')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def merchant_admin_required(view_func):
    """Restreint l'accès aux administrateurs et propriétaires"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        role = get_team_role(request.user)
        if role not in ('owner', 'admin'):
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('dashboard:overview')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def merchant_member_required(view_func):
    """Restreint l'accès à tout membre d'équipe (owner, admin, member)"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        role = get_team_role(request.user)
        if role is None:
            messages.error(request, "Vous devez faire partie d'une équipe.")
            return redirect('dashboard:overview')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
