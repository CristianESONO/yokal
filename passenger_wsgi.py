import os
import sys

# Add project directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Set dynamic settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yokal.settings')

# Import the WSGI application
from yokal.wsgi import application
