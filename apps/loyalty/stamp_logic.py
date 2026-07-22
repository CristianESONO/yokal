"""Logique de calcul des montants selon le type de programme."""


def compute_stamp_amount(program, raw_amount):
    """
    Calcule le montant à ajouter au solde de la carte.

    - visits  : 1 tampon par passage (points_per_unit, défaut 1)
    - points  : valeur saisie ou points_per_unit
    - spend   : montant d'achat saisi directement (ex. 2000 FCFA vers objectif 10000)
    """
    try:
        amount = float(raw_amount)
    except (TypeError, ValueError):
        amount = float(program.points_per_unit or 1)

    if program.program_type == 'visits':
        return float(program.points_per_unit or 1)

    if program.program_type == 'spend':
        if amount <= 0:
            raise ValueError('Le montant dépensé doit être supérieur à 0.')
        return amount

    return amount if amount > 0 else float(program.points_per_unit or 1)


def stamp_input_label(program):
    """Libellé du champ de saisie au scanner."""
    if program.program_type == 'spend':
        return f"Montant de l'achat ({program.currency_symbol})"
    if program.program_type == 'visits':
        return 'Nombre de tampons à ajouter'
    return f'Points à ajouter ({program.unit_label})'


def stamp_input_default(program):
    """Valeur par défaut du champ scanner."""
    if program.program_type == 'spend':
        return ''
    return int(program.points_per_unit or 1)


def threshold_label(program):
    """Libellé du seuil selon le type."""
    if program.program_type == 'spend':
        return f'Montant cible ({program.currency_symbol})'
    if program.program_type == 'visits':
        return 'Nombre de tampons requis'
    return 'Points requis pour la récompense'
