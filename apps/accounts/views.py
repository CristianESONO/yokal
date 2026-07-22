import logging
import os
import secrets
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.utils import timezone
from django.db import IntegrityError, transaction

from apps.accounts.models import TeamMember, MerchantProfile
from .forms import MerchantRegisterForm, AccountStepForm, BusinessStepForm, ProgramStepForm, DesignStepForm

logger = logging.getLogger(__name__)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:overview')
    
    step = request.GET.get('step', '1')
    steps = ['1', '2', '3', '4']
    
    if step not in steps:
        step = '1'
    
    # Get stored data from session
    wizard_data = request.session.get('wizard_data', {})
    
    if request.method == 'POST':
        if step == '1':
            form = AccountStepForm(request.POST)
            if form.is_valid():
                wizard_data['account'] = form.cleaned_data
                request.session['wizard_data'] = wizard_data
                return redirect(f'{request.path}?step=2')
        elif step == '2':
            form = BusinessStepForm(request.POST, request.FILES)
            if form.is_valid():
                # Store form data without the file in session
                business_data = form.cleaned_data.copy()
                if 'logo' in business_data and business_data['logo']:
                    # Save the file to temporary storage
                    logo_file = business_data['logo']
                    temp_path = default_storage.save(f'temp_logos/{logo_file.name}', logo_file)
                    request.session['temp_logo_path'] = temp_path
                    del business_data['logo']
                wizard_data['business'] = business_data
                request.session['wizard_data'] = wizard_data
                return redirect(f'{request.path}?step=3')
        elif step == '3':
            form = ProgramStepForm(request.POST)
            if form.is_valid():
                program_data = form.cleaned_data.copy()
                prog_type = program_data.get('program_type', 'stamps')
                
                if prog_type == 'stamps':
                    if not program_data.get('stamps_needed'):
                        program_data['stamps_needed'] = 10
                elif prog_type == 'points':
                    # Extract dynamic rewards from POST lists
                    dyn_points = request.POST.getlist('dyn_reward_points[]')
                    dyn_descs = request.POST.getlist('dyn_reward_descs[]')
                    if dyn_points and dyn_descs:
                        try:
                            program_data['stamps_needed'] = int(dyn_points[0])
                        except (ValueError, TypeError, IndexError):
                            program_data['stamps_needed'] = 50
                        program_data['reward_name'] = dyn_descs[0]
                    else:
                        program_data['stamps_needed'] = 50
                        program_data['reward_name'] = "Récompense"
                elif prog_type == 'spend':
                    # For spend: threshold = target amount in FCFA, reward = prize description
                    try:
                        program_data['stamps_needed'] = int(program_data.get('spend_threshold') or 10000)
                    except (ValueError, TypeError):
                        program_data['stamps_needed'] = 10000
                    if not program_data.get('reward_name'):
                        program_data['reward_name'] = "Récompense fidélité"
                
                wizard_data['program'] = program_data
                request.session['wizard_data'] = wizard_data
                return redirect(f'{request.path}?step=4')
        elif step == '4':
            form = DesignStepForm(request.POST)
            if form.is_valid():
                wizard_data['design'] = form.cleaned_data
                request.session['wizard_data'] = wizard_data

                account_data = wizard_data.get('account', {})
                business_data = wizard_data.get('business', {})
                program_data = wizard_data.get('program', {})
                design_data = wizard_data.get('design', {})

                if not account_data.get('email') or not account_data.get('password'):
                    messages.error(request, "Session expirée. Veuillez recommencer l'inscription.")
                    request.session.pop('wizard_data', None)
                    request.session.pop('temp_logo_path', None)
                    return redirect(f'{request.path}?step=1')

                if not business_data.get('business_name'):
                    messages.error(request, "Informations commerce manquantes. Reprenez à l'étape 2.")
                    return redirect(f'{request.path}?step=2')

                from django.contrib.auth.models import User
                from apps.loyalty.models import LoyaltyProgram

                username = account_data.get('email', '').lower()

                if User.objects.filter(username=username).exists():
                    messages.error(request, f"Un compte existe déjà avec l'adresse email {username}. Connectez-vous ou utilisez une autre adresse.")
                    request.session.pop('wizard_data', None)
                    return redirect('accounts:login')

                try:
                    with transaction.atomic():
                        user = User.objects.create_user(
                            username=username,
                            email=account_data.get('email', ''),
                            password=account_data.get('password', ''),
                            first_name=account_data.get('first_name', ''),
                            last_name=account_data.get('last_name', '')
                        )

                        merchant = MerchantProfile.objects.create(
                            user=user,
                            business_name=business_data.get('business_name', ''),
                            phone=account_data.get('phone', ''),
                        )

                        temp_logo_path = request.session.get('temp_logo_path')
                        if temp_logo_path and default_storage.exists(temp_logo_path):
                            from django.core.files import File
                            with default_storage.open(temp_logo_path, 'rb') as f:
                                merchant.logo.save(os.path.basename(temp_logo_path), File(f), save=True)

                        prog_type = program_data.get('program_type', 'stamps')
                        # Map form type to model type
                        if prog_type == 'stamps':
                            model_type = 'visits'
                        elif prog_type == 'points':
                            model_type = 'points'
                        else:  # spend
                            model_type = 'spend'

                        # Calculate secondary color from primary
                        primary_color = design_data.get('primary_color', '#3b82f6')
                        secondary_color = design_data.get('secondary_color')
                        if not secondary_color or secondary_color == '#2563eb':
                            try:
                                hex_val = primary_color.lstrip('#')
                                r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
                                r = max(0, int(r * 0.7))
                                g = max(0, int(g * 0.7))
                                b = max(0, int(b * 0.7))
                                secondary_color = f"#{r:02x}{g:02x}{b:02x}"
                            except Exception:
                                secondary_color = '#2563eb'

                        LoyaltyProgram.objects.create(
                            merchant=merchant,
                            name=f"Programme {business_data.get('business_name', 'Fidélité')}",
                            program_type=model_type,
                            reward_threshold=program_data.get('stamps_needed', 10),
                            reward_description=program_data.get('reward_name', '1 offre gratuite'),
                            # points_per_unit = points earned per visit (for 'points' type)
                            points_per_unit=program_data.get('points_per_visit', 1) if prog_type == 'points' else 1,
                            currency='XOF',  # Default to FCFA for West African market
                            color_primary=primary_color,
                            color_secondary=secondary_color,
                        )

                    # Only clean up files / sessions outside of atomic transaction to handle retry cleanly
                    if temp_logo_path and default_storage.exists(temp_logo_path):
                        try:
                            default_storage.delete(temp_logo_path)
                        except Exception:
                            pass
                        request.session.pop('temp_logo_path', None)

                    login(request, user)
                    messages.success(request, f"Bienvenue {merchant.business_name} ! Votre compte est créé.")
                    request.session.pop('wizard_data', None)
                    return redirect('dashboard:overview')

                except IntegrityError:
                    messages.error(request, f"Un compte existe déjà avec l'adresse email {username}. Connectez-vous ou utilisez une autre adresse.")
                    request.session.pop('wizard_data', None)
                    return redirect('accounts:login')
                except Exception:
                    logger.exception("Erreur lors de la création de compte (étape 4)")
                    messages.error(request, "Une erreur est survenue lors de la création du compte. Veuillez réessayer.")
                    return redirect(f'{request.path}?step=4')
    else:
        if step == '1':
            form = AccountStepForm(initial=wizard_data.get('account', {}))
        elif step == '2':
            form = BusinessStepForm(initial=wizard_data.get('business', {}))
        elif step == '3':
            form = ProgramStepForm(initial=wizard_data.get('program', {}))
        elif step == '4':
            form = DesignStepForm(initial=wizard_data.get('design', {}))
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'step': step,
        'wizard_data': wizard_data,
        'predefined_colors': DesignStepForm.PREDEFINED_COLORS
    })


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_overview')
        return redirect('dashboard:overview')

    next_url = request.GET.get('next', '') or request.POST.get('next', '')
    is_admin_login = next_url.startswith('/admin')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                return redirect(next_url or 'admin_overview')
            return redirect(next_url or 'dashboard:overview')
        messages.error(request, "Identifiants incorrects.")
    else:
        form = AuthenticationForm()

    template = 'accounts/admin_login.html' if is_admin_login else 'accounts/login.html'
    return render(request, template, {'form': form})


def logout_view(request):
    logout(request)
    return redirect('loyalty:landing')


# ========================
# TEAM MANAGEMENT VIEWS
# ========================

@login_required
def join_team(request, token):
    """Accepter une invitation d'équipe"""
    team_member = get_object_or_404(TeamMember, invitation_token=token, status='pending')
    
    # Vérifier si token expiré (7 jours)
    if timezone.now() - team_member.invitation_sent_at > datetime.timedelta(days=7):
        messages.error(request, "❌ Cette invitation a expiré")
        return redirect('loyalty:landing')
    
    if request.user.is_authenticated:
        # Utilisateur connecté
        if request.user.email == team_member.email:
            team_member.user = request.user
            team_member.status = 'active'
            team_member.joined_at = timezone.now()
            team_member.invitation_token = None
            team_member.save()
            messages.success(request, f"✅ Vous avez rejoint {team_member.merchant.business_name}!")
            return redirect('dashboard:overview')
        else:
            messages.error(request, f"❌ Veuillez vous connecter avec {team_member.email}")
            return redirect('accounts:logout')
    
    # Utilisateur non connecté - afficher formulaire login
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.email == team_member.email:
                login(request, user)
                team_member.user = user
                team_member.status = 'active'
                team_member.joined_at = timezone.now()
                team_member.invitation_token = None
                team_member.save()
                messages.success(request, f"✅ Bienvenue dans {team_member.merchant.business_name}!")
                return redirect('dashboard:overview')
            else:
                messages.error(request, f"❌ Cet email ne correspond pas à l'invitation")
        else:
            messages.error(request, "❌ Identifiants incorrects")
    else:
        form = AuthenticationForm()
    
    context = {
        'team_member': team_member,
        'token': token,
        'form': form,
    }
    return render(request, 'accounts/join_team.html', context)


def send_invitation_email(email, merchant_name, role, token):
    """Envoyer email d'invitation"""
    role_display = dict(TeamMember.ROLE_CHOICES).get(role, role)
    invitation_link = f"{django_settings.SITE_URL}/accounts/join-team/{token}/"

    subject = f"Rejoignez {merchant_name} sur Yokalma"

    message = f"""
Bonjour,

Vous avez été invité à rejoindre l'équipe de {merchant_name} sur Yokalma.

Rôle : {role_display}

Cliquez sur le lien ci-dessous pour accepter l'invitation :
{invitation_link}

Ce lien expire dans 7 jours.

---
Yokalma - Solution de fidélité
"""

    try:
        send_mail(
            subject,
            message,
            django_settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"❌ Erreur envoi email : {e}")


@login_required
def invite_team(request):
    """Inviter un membre d'équipe"""
    from apps.accounts.utils import get_merchant

    merchant = get_merchant(request.user)
    if not merchant:
        messages.error(request, "Vous n'avez pas de commerce associé.")
        return redirect('dashboard:overview')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        role = request.POST.get('role', 'member')

        if not email:
            messages.error(request, "L'email est requis.")
            return redirect('dashboard:settings')

        # Vérifier si déjà invité
        if TeamMember.objects.filter(merchant=merchant, email=email).exists():
            messages.warning(request, "Cet email a déjà été invité.")
            return redirect('dashboard:settings')

        # Créer l'invitation
        token = secrets.token_urlsafe(32)
        TeamMember.objects.create(
            merchant=merchant,
            email=email,
            role=role,
            status='pending',
            invitation_token=token,
            invitation_sent_at=timezone.now()
        )

        # Envoyer l'email
        send_invitation_email(email, merchant.business_name, role, token)
        messages.success(request, f"✅ Invitation envoyée à {email}")

    return redirect('dashboard:settings')


@login_required
def cancel_invitation(request, member_id):
    """Annuler une invitation en attente"""
    from apps.accounts.utils import get_merchant

    merchant = get_merchant(request.user)
    if not merchant:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard:overview')

    member = get_object_or_404(TeamMember, id=member_id, merchant=merchant, status='pending')
    member.delete()
    messages.success(request, "✅ Invitation annulée.")
    return redirect('dashboard:settings')


@login_required
def remove_team_member(request, member_id):
    """Retirer un membre actif de l'équipe"""
    from apps.accounts.utils import get_merchant

    merchant = get_merchant(request.user)
    if not merchant:
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard:overview')

    member = get_object_or_404(TeamMember, id=member_id, merchant=merchant, status='active')
    member.delete()
    messages.success(request, "✅ Membre retiré de l'équipe.")
    return redirect('dashboard:settings')
