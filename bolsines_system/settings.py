"""
Configuración Django — Sistema Bolsines
Grupo 5 · PPAI 2026 · UTN DSI
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-grupo5-bolsines-2026')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'bolsines',  # primero: su comando runserver debe reemplazar al de staticfiles
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bolsines_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bolsines_system.wsgi.application'

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

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# GPS Tracker config (via .env)
GPS_API_BASE_URL = os.getenv('GPS_API_BASE_URL', 'http://localhost:8080')
GPS_API_KEYS = {
    'XTR4500L': os.getenv('GPS_API_KEY_XTR4500L', 'sk_xtr_9F3a7C21bE6d4A10f2c8e5b7d913'),
    'NAVTRACKQX7A': os.getenv('GPS_API_KEY_NAVTRACKQX7A', 'sk_nav_7b61d9e4c3a2485fae10c77d5b2f'),
    'GEOPULSEMTR900': os.getenv('GPS_API_KEY_GEOPULSEMTR900', 'sk_geo_f2d84a1c9e7345b8a6d1c3f0972e'),
}
GPS_MODEL_DEFAULT = os.getenv('GPS_MODEL_DEFAULT', 'XTR4500L')

# Correo (CU 30). Por defecto sale por consola; configurar SMTP (Gmail) en .env para envío real.
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')  # contraseña de aplicación de Google
EMAIL_TIMEOUT = 15
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'bolsines@sistema.local')
# Modo prueba: si tiene valor, todos los correos van a esta casilla en lugar de a los gerentes reales.
EMAIL_REDIRIGIR_A = os.getenv('EMAIL_REDIRIGIR_A', '').strip()

# Google Maps
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
GOOGLE_MAPS_MAP_ID = os.getenv('GOOGLE_MAPS_MAP_ID', 'DEMO_MAP_ID')  # necesario para AdvancedMarkerElement
