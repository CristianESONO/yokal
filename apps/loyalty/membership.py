from django.utils import timezone

from apps.wallet.services import create_loyalty_object
from .models import LoyaltyCard


def needs_membership_approval(merchant, *, auto_approve=False):
    return merchant.require_membership_approval and not auto_approve


def initial_membership_state(merchant, *, auto_approve=False):
    if needs_membership_approval(merchant, auto_approve=auto_approve):
        return 'pending', False
    return 'approved', True


def enroll_customer(program, customer_name, customer_phone='', customer_email='', *, auto_approve=False):
    """Crée ou retourne une carte pour un programme. Retourne (carte, created)."""
    existing = LoyaltyCard.objects.filter(
        program=program,
        customer_phone=customer_phone,
        is_deleted=False,
    ).first()
    if existing:
        return existing, False

    status, is_active = initial_membership_state(program.merchant, auto_approve=auto_approve)
    card = LoyaltyCard.objects.create(
        program=program,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        membership_status=status,
        is_active=is_active,
    )
    if status == 'approved':
        create_loyalty_object(card)
    return card, True


def approve_membership(card, user):
    card.membership_status = 'approved'
    card.is_active = True
    card.approved_at = timezone.now()
    card.approved_by = user
    card.save(update_fields=['membership_status', 'is_active', 'approved_at', 'approved_by', 'updated_at'])
    create_loyalty_object(card)
    return card


def reject_membership(card):
    card.membership_status = 'rejected'
    card.is_active = False
    card.save(update_fields=['membership_status', 'is_active', 'updated_at'])
    return card


def revoke_membership(card):
    card.membership_status = 'revoked'
    card.is_active = False
    card.save(update_fields=['membership_status', 'is_active', 'updated_at'])
    return card
