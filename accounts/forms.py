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
