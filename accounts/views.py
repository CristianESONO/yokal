from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import MerchantRegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:overview')
    if request.method == 'POST':
        form = MerchantRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.merchant_profile.business_name} ! Votre compte est créé.")
            return redirect('dashboard:overview')
    else:
        form = MerchantRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:overview')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard:overview'))
        messages.error(request, "Identifiants incorrects.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('loyalty:landing')
