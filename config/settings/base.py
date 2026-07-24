import os
import pymysql
from pathlib import Path
from dotenv import load_dotenv

pymysql.install_as_MySQLdb()
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

# URL du site vitrine (Next.js). La landing publique est servie par Next désormais :
# le '/' de Django et les redirects "accueil" pointent ici.
# Local : http://localhost:3000 — Prod : https://yokalma.com
VITRINE_URL = os.getenv('VITRINE_URL', 'http://localhost:3000')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'apps.accounts',
    'apps.loyalty',
    'apps.wallet',
    'apps.dashboard',
    'apps.api',
    'apps.billing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.dashboard.context_processors.dashboard_program',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

if os.getenv('DATABASE_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DATABASE_NAME'),
            'USER': os.getenv('DATABASE_USER'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD'),
            'HOST': os.getenv('DATABASE_HOST', 'localhost'),
            'PORT': os.getenv('DATABASE_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Dakar'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

GOOGLE_WALLET_ISSUER_ID = os.getenv('GOOGLE_WALLET_ISSUER_ID', '')
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', '')
GOOGLE_WALLET_CLASS_PREFIX = 'yokal_loyalty'
DEFAULT_WALLET_LOGO_URL = os.getenv('DEFAULT_WALLET_LOGO_URL', '')

# Apple Wallet (PassKit) Configuration
APPLE_PASS_TYPE_ID = os.getenv('APPLE_PASS_TYPE_ID', '')
APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID', '')
APPLE_CERTIFICATE_PATH = os.getenv('APPLE_CERTIFICATE_PATH', '')
APPLE_CERTIFICATE_PASSWORD = os.getenv('APPLE_CERTIFICATE_PASSWORD', '')
APPLE_WWDR_CERT_PATH = os.getenv('APPLE_WWDR_CERT_PATH', '')

EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY', '')

# Evolution API (WhatsApp Gateway) - Global platform config
EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL', '')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY', '')

SITE_URL = os.getenv('SITE_URL', 'https://yokalma.com')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@yokalma.com')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'noreply@yokalma.com')
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# PayTech (paiements abonnements)
PAYTECH_API_KEY = os.getenv('PAYTECH_API_KEY', '')
PAYTECH_API_SECRET = os.getenv('PAYTECH_API_SECRET', '')
PAYTECH_BASE_URL = os.getenv('PAYTECH_BASE_URL', 'https://paytech.sn/api').rstrip('/')
PAYTECH_ENV = os.getenv('PAYTECH_ENV', 'test')

CSRF_TRUSTED_ORIGINS = [
    "https://yokalma.com",
    "https://www.yokalma.com",
    "https://yokalma.linkup.sn",
]

