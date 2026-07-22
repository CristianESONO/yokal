import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


def generate_invitation_token():
    """Génère un token unique pour l'invitation."""
    return secrets.token_urlsafe(32)


def send_team_invitation(team_member):
    """
    Envoie un email d'invitation à un membre d'équipe.
    """
    merchant = team_member.merchant
    user = merchant.user
    
    # Générer le token si nécessaire
    if not team_member.invitation_token:
        team_member.invitation_token = generate_invitation_token()
        team_member.invitation_sent_at = timezone.now()
        team_member.save(update_fields=['invitation_token', 'invitation_sent_at'])
    
    # Construire l'URL d'acceptation
    invitation_url = f"{settings.SITE_URL}/accounts/join-team/{team_member.invitation_token}/"
    
    # Préparer l'email
    subject = f"Invitation à rejoindre l'équipe {merchant.business_name} sur Yokalma"
    message = f"""
Bonjour,

{user.get_full_name() or user.email} vous invite à rejoindre l'équipe de {merchant.business_name} sur Yokalma.

Rôle : {team_member.get_role_display()}

Pour accepter l'invitation, cliquez sur le lien suivant :
{invitation_url}

Ce lien expirera dans 7 jours.

Si vous n'avez pas demandé cette invitation, vous pouvez ignorer cet email.

— L'équipe Yokalma
"""
    
    # Envoyer l'email
    if team_member.email:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [team_member.email],
            fail_silently=False,
        )
        return True
    return False


def accept_team_invitation(token, user):
    """
    Accepte une invitation d'équipe et lie l'utilisateur au marchand.
    """
    from apps.accounts.models import TeamMember
    
    try:
        team_member = TeamMember.objects.get(
            invitation_token=token,
            status='pending'
        )
    except TeamMember.DoesNotExist:
        return None, "Invitation introuvable ou déjà acceptée."
    
    # Vérifier que l'email correspond
    if team_member.email != user.email:
        return None, "L'email de l'invitation ne correspond pas à votre compte."
    
    # Mettre à jour le membre d'équipe
    team_member.user = user
    team_member.status = 'active'
    team_member.joined_at = timezone.now()
    team_member.invitation_token = None
    team_member.save(update_fields=['user', 'status', 'joined_at', 'invitation_token'])
    
    return team_member, None
