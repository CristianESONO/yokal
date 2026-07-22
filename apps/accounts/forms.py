from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import MerchantProfile


class MerchantRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse email")
    business_name = forms.CharField(max_length=150, label="Nom du commerce")
    phone = forms.CharField(max_length=20, required=False, label="Téléphone (optionnel)")

    class Meta:
        model = User
        fields = ['username', 'email', 'business_name', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            MerchantProfile.objects.create(
                user=user,
                business_name=self.cleaned_data['business_name'],
                phone=self.cleaned_data.get('phone', ''),
            )
        return user


# Multi-step wizard forms
class AccountStepForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(max_length=20, required=True, label="Téléphone")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Mot de passe", min_length=6)


class BusinessStepForm(forms.Form):
    business_name = forms.CharField(max_length=150, required=True, label="Nom du commerce")
    logo = forms.ImageField(required=False, label="Logo")


class ProgramStepForm(forms.Form):
    PROGRAM_TYPE_CHOICES = [
        ('stamps', 'Tampons'),
        ('points', 'Points'),
        ('spend', 'Montant dépensé (FCFA)'),
    ]
    program_type = forms.ChoiceField(
        choices=PROGRAM_TYPE_CHOICES, required=True,
        label="Type de programme", initial='stamps'
    )
    # --- Stamps fields ---
    stamps_needed = forms.IntegerField(
        min_value=3, max_value=50, required=False,
        label="Nombre de tampons requis", initial=10
    )
    reward_name = forms.CharField(
        max_length=100, required=False,
        label="Nom de la récompense", initial="1 café offert"
    )
    unit_label = forms.CharField(
        max_length=20, required=False,
        label="Nom des tampons", initial="tampons"
    )
    # --- Points fields ---
    points_per_visit = forms.IntegerField(
        min_value=1, required=False,
        label="Points par visite", initial=1,
        help_text="Combien de points le client gagne à chaque passage au scanner"
    )
    # Dynamic reward tiers handled via JS (dyn_reward_points[] / dyn_reward_descs[])

    # --- Spend (Montant dépensé FCFA) fields ---
    spend_threshold = forms.IntegerField(
        min_value=1000, required=False,
        label="Objectif à atteindre (FCFA)", initial=10000,
        help_text="Ex: 10000 = le client reçoit une récompense quand il a dépensé 10 000 FCFA"
    )


class DesignStepForm(forms.Form):
    PREDEFINED_COLORS = [
        '#3b82f6', '#2563eb', '#8b5cf6', '#a855f7', '#ec4899', '#f43f5e',
        '#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e', '#14b8a6',
        '#06b6d4', '#0ea5e9', '#6366f1', '#64748b'
    ]
    primary_color = forms.CharField(max_length=7, required=False, label="Couleur principale", initial="#3b82f6")
    secondary_color = forms.CharField(max_length=7, required=False, label="Couleur secondaire", initial="#2563eb")
