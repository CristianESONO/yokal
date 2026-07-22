SESSION_PROGRAM_KEY = 'active_program_id'


def get_merchant_programs(merchant):
    return merchant.programs.filter(active=True).order_by('-created_at')


def get_current_program(request, merchant):
    """Programme actif (session ou ?program=). Met à jour la session."""
    programs = get_merchant_programs(merchant)
    program_id = request.GET.get('program') or request.session.get(SESSION_PROGRAM_KEY)
    program = merchant.get_program(program_id) if program_id else merchant.program
    if program:
        request.session[SESSION_PROGRAM_KEY] = program.id
    return program, programs


def program_query(request, extra=None):
    """Suffixe ?program=id pour conserver le contexte dans les liens."""
    program_id = request.session.get(SESSION_PROGRAM_KEY)
    if not program_id:
        return ''
    q = f'program={program_id}'
    if extra:
        return f'?{q}&{extra}'
    return f'?{q}'
