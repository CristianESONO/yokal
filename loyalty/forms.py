from django import forms
from .models import LoyaltyProgram, LoyaltyCard


class LoyaltyProgramForm(forms.ModelForm):
    class Meta:
        model = LoyaltyProgram
        fields = [
            'name', 'program_type', 'card_template', 'reward_threshold', 'points_per_unit',
            'reward_description', 'color_primary', 'color_secondary', 'logo'
        ]
        widgets = {
            'color_primary': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_secondary': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'program_type': forms.Select(attrs={'class': 'form-select'}),
            'card_template': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': 'Nom du programme',
            'program_type': 'Type de programme de fidélité',
            'reward_threshold': 'Seuil pour une récompense (points ou tampons)',
            'points_per_unit': 'Valeur par transaction (ex: 1 visite = 1 point)',
            'reward_description': 'Description de la récompense',
            'color_primary': 'Couleur principale',
            'color_secondary': 'Couleur secondaire',
            'logo': 'Logo du commerce',
        }


class LoyaltyCardForm(forms.ModelForm):
    class Meta:
        model = LoyaltyCard
        fields = ['customer_name', 'customer_phone']
        labels = {
            'customer_name': 'Nom du client',
            'customer_phone': 'Téléphone (pour WhatsApp)',
        }
