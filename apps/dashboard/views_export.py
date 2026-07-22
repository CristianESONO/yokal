"""
Export functionality for dashboard (CSV, Excel, etc.)
"""

import csv
import datetime
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.accounts.utils import get_merchant


@login_required
def export_customers_csv(request):
    """Export customer cards to CSV."""
    merchant = get_merchant(request.user)
    if not merchant:
        return HttpResponse("Commerce non trouvé", status=404)
    
    from apps.dashboard.utils import get_current_program
    program, _ = get_current_program(request, merchant)
    
    if not program:
        return HttpResponse("Aucun programme de fidélité trouvé", status=404)
    
    # Get all cards for this program
    cards = program.cards.filter(is_deleted=False).select_related('program', 'program__merchant')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="clients_{program.name}_{datetime.date.today()}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Nom du client',
        'Téléphone',
        'Email',
        'Solde actuel',
        'Cumul total',
        'Seuil récompense',
        'Récompense prête',
        'Date de création',
        'Dernière activité',
    ])
    
    # Write data
    for card in cards:
        last_activity = card.history.order_by('-stamped_at').first()
        last_activity_date = last_activity.stamped_at.strftime('%d/%m/%Y %H:%M') if last_activity else 'Jamais'
        
        writer.writerow([
            card.customer_name,
            card.customer_phone or '',
            card.customer_email or '',
            card.balance,
            card.total_accumulated,
            card.program.reward_threshold,
            'Oui' if card.is_reward_ready else 'Non',
            card.created_at.strftime('%d/%m/%Y %H:%M'),
            last_activity_date,
        ])
    
    return response


@login_required
def export_transactions_csv(request):
    """Export transaction history to CSV."""
    merchant = get_merchant(request.user)
    if not merchant:
        return HttpResponse("Commerce non trouvé", status=404)
    
    from apps.dashboard.utils import get_current_program
    program, _ = get_current_program(request, merchant)
    
    if not program:
        return HttpResponse("Aucun programme de fidélité trouvé", status=404)
    
    # Get all transactions for this program
    from apps.loyalty.models import StampHistory
    transactions = StampHistory.objects.filter(
        card__program=program
    ).select_related('card', 'card__program', 'stamped_by').order_by('-stamped_at')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="transactions_{program.name}_{datetime.date.today()}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Date',
        'Client',
        'Type',
        'Montant',
        'Tamponeur',
        'Programme',
    ])
    
    # Write data
    for tx in transactions:
        writer.writerow([
            tx.stamped_at.strftime('%d/%m/%Y %H:%M'),
            tx.card.customer_name,
            tx.get_transaction_type_display(),
            tx.amount,
            tx.stamped_by.get_full_name() if tx.stamped_by else 'Système',
            tx.card.program.name,
        ])
    
    return response


@login_required
def export_rewards_csv(request):
    """Export rewards to CSV."""
    merchant = get_merchant(request.user)
    if not merchant:
        return HttpResponse("Commerce non trouvé", status=404)
    
    from apps.dashboard.utils import get_current_program
    program, _ = get_current_program(request, merchant)
    
    if not program:
        return HttpResponse("Aucun programme de fidélité trouvé", status=404)
    
    # Get all rewards for this program
    from apps.loyalty.models import Reward
    rewards = Reward.objects.filter(
        card__program=program
    ).select_related('card', 'card__program').order_by('-created_at')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="recompenses_{program.name}_{datetime.date.today()}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Date de création',
        'Client',
        'Description',
        'Valeur',
        'Statut',
        'Date d\'utilisation',
    ])
    
    # Write data
    for reward in rewards:
        writer.writerow([
            reward.created_at.strftime('%d/%m/%Y %H:%M'),
            reward.card.customer_name,
            reward.description,
            reward.value,
            'Utilisé' if reward.redeemed else 'En attente',
            reward.redeemed_at.strftime('%d/%m/%Y %H:%M') if reward.redeemed_at else '',
        ])
    
    return response
