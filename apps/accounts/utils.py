from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from apps.accounts.models import MerchantProfile, TeamMember


def get_merchant(user):
    """Return the merchant profile for an owner or active team member."""
    if not user or not user.is_authenticated:
        return None
    try:
        return user.merchant_profile
    except MerchantProfile.DoesNotExist:
        pass
    membership = (
        TeamMember.objects.filter(user=user, status='active')
        .select_related('merchant')
        .first()
    )
    return membership.merchant if membership else None


def get_team_role(user):
    """Return the effective role of the user for the merchant.
    
    Returns 'owner' if the user owns the MerchantProfile directly,
    or the TeamMember.role if they are an active team member.
    Returns None if not authenticated or not associated with any merchant.
    """
    if not user or not user.is_authenticated:
        return None
    try:
        user.merchant_profile  # has their own profile → owner
        return 'owner'
    except MerchantProfile.DoesNotExist:
        pass
    membership = (
        TeamMember.objects.filter(user=user, status='active')
        .first()
    )
    return membership.role if membership else None


def admin_required(view_func):
    """Decorator: allow owner and admin team members only. Block 'member' role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        role = get_team_role(request.user)
        if role not in ('owner', 'admin'):
            messages.error(request, "⛔ Accès réservé aux administrateurs.")
            return redirect('dashboard:overview')
        return view_func(request, *args, **kwargs)
    return wrapper


def owner_required(view_func):
    """Decorator: allow the merchant owner only (not team members)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        role = get_team_role(request.user)
        if role != 'owner':
            messages.error(request, "⛔ Accès réservé au propriétaire du compte.")
            return redirect('dashboard:overview')
        return view_func(request, *args, **kwargs)
    return wrapper
