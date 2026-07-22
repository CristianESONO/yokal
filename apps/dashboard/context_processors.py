from .utils import get_current_program, program_query


def dashboard_program(request):
    if not request.user.is_authenticated:
        return {}
    try:
        merchant = request.user.merchant_profile
    except Exception:
        return {}

    program, programs = get_current_program(request, merchant)
    return {
        'current_program': program,
        'merchant_programs': programs,
        'program_qs': program_query(request),
    }
