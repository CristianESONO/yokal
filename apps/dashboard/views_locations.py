"""
Location management views for multi-point of sale support.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.accounts.utils import get_merchant
from apps.accounts.models_location import Location


@login_required
def locations_list(request):
    """List all locations for the merchant."""
    merchant = get_merchant(request.user)
    if not merchant:
        return redirect('dashboard:overview')
    
    locations = merchant.locations.all()
    
    context = {
        'locations': locations,
    }
    
    return render(request, 'dashboard/locations_list.html', context)


@login_required
def location_create(request):
    """Create a new location."""
    merchant = get_merchant(request.user)
    if not merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        is_main = request.POST.get('is_main') == 'on'
        
        if not name:
            return JsonResponse({'error': 'Nom requis'}, status=400)
        
        location = Location.objects.create(
            merchant=merchant,
            name=name,
            address=address,
            city=city,
            phone=phone,
            email=email,
            is_main=is_main
        )
        
        messages.success(request, f'Point de vente "{name}" créé avec succès')
        return JsonResponse({'success': True, 'redirect': '/dashboard/settings/locations/'})
    
    return render(request, 'dashboard/location_form.html')


@login_required
def location_edit(request, location_id):
    """Edit an existing location."""
    merchant = get_merchant(request.user)
    if not merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    location = get_object_or_404(Location, pk=location_id, merchant=merchant)
    
    if request.method == 'POST':
        location.name = request.POST.get('name')
        location.address = request.POST.get('address', '')
        location.city = request.POST.get('city', '')
        location.phone = request.POST.get('phone', '')
        location.email = request.POST.get('email', '')
        location.is_main = request.POST.get('is_main') == 'on'
        location.is_active = request.POST.get('is_active') == 'on'
        
        if not location.name:
            return JsonResponse({'error': 'Nom requis'}, status=400)
        
        location.save()
        
        messages.success(request, f'Point de vente "{location.name}" mis à jour')
        return JsonResponse({'success': True, 'redirect': '/dashboard/settings/locations/'})
    
    context = {
        'location': location,
    }
    
    return render(request, 'dashboard/location_form.html', context)


@login_required
def location_delete(request, location_id):
    """Delete a location."""
    merchant = get_merchant(request.user)
    if not merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    location = get_object_or_404(Location, pk=location_id, merchant=merchant)
    
    if location.is_main:
        return JsonResponse({'error': 'Impossible de supprimer le siège principal'}, status=400)
    
    location.delete()
    
    messages.success(request, 'Point de vente supprimé')
    return JsonResponse({'success': True, 'redirect': '/dashboard/settings/locations/'})
