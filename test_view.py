import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from apps.dashboard.views import super_admin_overview
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage

# Create dummy request
factory = RequestFactory()
request = factory.get('/admin/')

# Add session
middleware = SessionMiddleware(lambda r: None)
middleware.process_request(request)
request.session.save()

# Add messages
request._messages = FallbackStorage(request)

# Create a mock staff user
user = User(username='test_admin', is_staff=True, is_active=True)
# Mock is_authenticated attribute-based check (Django 1.10+ uses attribute is_authenticated)
# In Django it is a property/attribute so we can mock/override it
user.id = 99999
user.email = 'admin@example.com'

request.user = user
print(f"Testing view with user: {user.username}, is_staff: {user.is_staff}, is_authenticated: {user.is_authenticated}")

try:
    response = super_admin_overview(request)
    print(f"Response status: {response.status_code}")
    if hasattr(response, 'url'):
        print(f"Redirects to: {response.url}")
    if response.status_code == 200:
        print("SUCCESS! Rendering template content...")
        if hasattr(response, 'render') and callable(response.render):
            response.render()
        print("Render complete! Contents:")
        print(response.content[:800].decode('utf-8', errors='ignore'))
except Exception as e:
    import traceback
    traceback.print_exc()
