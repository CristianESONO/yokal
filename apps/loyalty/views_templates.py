"""
Template views for program templates.
"""

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from apps.loyalty.models import ProgramTemplate
from apps.accounts.utils import get_merchant
from django.shortcuts import get_object_or_404


@csrf_exempt
def get_templates(request):
    """Get all available program templates."""
    try:
        templates = ProgramTemplate.objects.filter(is_active=True)
        templates_data = []
        for template in templates:
            templates_data.append({
                'id': template.id,
                'business_type': template.business_type,
                'name': template.name,
                'description': template.description,
                'program_type': template.program_type,
                'reward_threshold': template.reward_threshold,
                'reward_description': template.reward_description,
                'reward_value': str(template.reward_value),
                'unit_label': template.unit_label,
                'color_primary': template.color_primary,
                'color_secondary': template.color_secondary,
                'card_template': template.card_template,
            })
        return JsonResponse({'templates': templates_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def apply_template(request, template_id):
    """Apply a template to a program."""
    merchant = get_merchant(request.user)
    if not merchant:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    template = get_object_or_404(ProgramTemplate, pk=template_id, is_active=True)
    
    return JsonResponse({
        'success': True,
        'template': {
            'program_type': template.program_type,
            'reward_threshold': template.reward_threshold,
            'reward_description': template.reward_description,
            'reward_value': str(template.reward_value),
            'unit_label': template.unit_label,
            'color_primary': template.color_primary,
            'color_secondary': template.color_secondary,
            'card_template': template.card_template,
        }
    })
