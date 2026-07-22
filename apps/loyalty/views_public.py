from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.urls import reverse

from apps.accounts.models import MerchantProfile
from apps.loyalty.models import LoyaltyProgram
from apps.loyalty.forms import MerchantEnrollForm
from apps.loyalty.membership import enroll_customer


def merchant_public_page(request, merchant_slug):
    """Public landing page for a merchant (SEO local)."""
    merchant = get_object_or_404(MerchantProfile, slug=merchant_slug)

    programs = merchant.programs.filter(active=True)

    if not programs.exists():
        raise Http404("Aucun programme de fidélité actif")

    program = programs.first()

    context = {
        'merchant': merchant,
        'program': program,
        'programs': programs,
        'meta_title': f"{merchant.business_name} - Programme de fidélité Yokalma",
        'meta_description': f"Rejoignez le programme de fidélité {merchant.business_name} et gagnez des récompenses !",
    }

    return render(request, 'loyalty/public_merchant.html', context)


def merchant_self_enroll(request, merchant_slug):
    """Adhésion globale : choix d'un ou plusieurs programmes puis formulaire."""
    merchant = get_object_or_404(MerchantProfile, slug=merchant_slug)
    programs = merchant.programs.filter(active=True).order_by('name')

    if not programs.exists():
        raise Http404("Aucun programme de fidélité actif")

    from apps.billing.services import ensure_merchant_subscription
    sub = ensure_merchant_subscription(merchant)
    subscription_invalid = bool(sub and not sub.is_compliant)

    if request.method == 'POST' and not subscription_invalid:
        form = MerchantEnrollForm(request.POST, merchant=merchant)
        if form.is_valid():
            name = form.cleaned_data['customer_name']
            phone = form.cleaned_data['customer_phone']
            email = form.cleaned_data['customer_email']
            selected_programs = form.cleaned_data['programs']

            created_cards = []
            existing_cards = []

            for program in selected_programs:
                card, created = enroll_customer(
                    program,
                    customer_name=name,
                    customer_phone=phone,
                    customer_email=email,
                )
                if created:
                    created_cards.append(card)
                else:
                    existing_cards.append(card)

            all_cards = created_cards + existing_cards
            if not all_cards:
                messages.error(request, "Aucune carte n'a pu être créée.")
            elif len(all_cards) == 1 and all_cards[0].is_membership_usable and not created_cards:
                messages.info(request, "Bienvenue ! Voici votre carte existante.")
                return redirect('loyalty:customer_card', token=str(all_cards[0].qr_token))
            elif len(all_cards) == 1 and len(created_cards) == 1 and created_cards[0].is_membership_usable:
                messages.success(request, "Félicitations ! Votre carte est prête.")
                return redirect('loyalty:customer_card', token=str(created_cards[0].qr_token))
            else:
                pending = any(c.is_pending_membership for c in all_cards)
                return render(request, 'loyalty/enroll_success.html', {
                    'merchant': merchant,
                    'cards': all_cards,
                    'created_count': len(created_cards),
                    'pending': pending,
                })
    else:
        form = MerchantEnrollForm(merchant=merchant)
        if programs.count() == 1:
            form.fields['programs'].initial = [programs.first().pk]

    return render(request, 'loyalty/merchant_enroll.html', {
        'merchant': merchant,
        'programs': programs,
        'form': form,
        'subscription_invalid': subscription_invalid,
    })


def program_public_page(request, merchant_slug, program_slug):
    """Public page for a specific loyalty program."""
    merchant = get_object_or_404(MerchantProfile, slug=merchant_slug)
    program = get_object_or_404(
        LoyaltyProgram,
        slug=program_slug,
        merchant=merchant,
        active=True
    )

    context = {
        'merchant': merchant,
        'program': program,
        'meta_title': f"{program.name} - {merchant.business_name}",
        'meta_description': program.description or f"Découvrez le programme de fidélité {program.name} chez {merchant.business_name}",
    }

    return render(request, 'loyalty/public_program.html', context)
