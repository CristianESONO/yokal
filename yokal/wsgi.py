"""
WSGI config for yokal project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yokal.settings')
application = get_wsgi_application()
