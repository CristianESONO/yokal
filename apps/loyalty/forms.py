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
            'points_per_unit': forms.HiddenInput(),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['points_per_unit'].required = False
        self.fields['points_per_unit'].localize = True
        if not self.initial.get('points_per_unit') and not self.data.get('points_per_unit'):
            self.initial['points_per_unit'] = 1.0

    def clean_points_per_unit(self):
        value = self.cleaned_data.get('points_per_unit')
        return value if value is not None else 1.0


class LoyaltyCardForm(forms.ModelForm):
    class Meta:
        model = LoyaltyCard
        fields = ['customer_name', 'customer_phone', 'customer_email']
        labels = {
            'customer_name': 'Nom du client',
            'customer_phone': 'Téléphone (pour WhatsApp)',
            'customer_email': 'Email (pour Google Wallet)',
        }


class MerchantEnrollForm(forms.Form):
    customer_name = forms.CharField(
        max_length=150,
        label='Nom complet',
        widget=forms.TextInput(attrs={'placeholder': 'Marie Dupont', 'class': 'form-input'}),
    )
    customer_phone = forms.CharField(
        max_length=20,
        label='Téléphone',
        widget=forms.TextInput(attrs={'placeholder': '77 000 00 00', 'class': 'form-input'}),
    )
    customer_email = forms.EmailField(
        required=False,
        label='Email (optionnel)',
        widget=forms.EmailInput(attrs={'placeholder': 'marie@exemple.com', 'class': 'form-input'}),
    )
    programs = forms.ModelMultipleChoiceField(
        queryset=LoyaltyProgram.objects.none(),
        label='Programmes',
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, merchant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if merchant:
            self.fields['programs'].queryset = merchant.programs.filter(active=True).order_by('name')

    def clean_programs(self):
        programs = self.cleaned_data.get('programs')
        if not programs:
            raise forms.ValidationError('Sélectionnez au moins un programme.')
        return programs
