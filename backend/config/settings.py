"""
Django settings for Damasco Gift Cards Portal.
"""

import os
import secrets
import warnings
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def env_list(name, default):
    """Lista separada por comas desde .env (ej: HOSTS=a.com,b.com)."""
    return [v.strip() for v in os.getenv(name, default).split(',') if v.strip()]


# Firma las sesiones de clientes y caja: en producción DEBE venir de .env.
# Sin ella se genera una al arrancar (las sesiones se pierden al reiniciar).
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(50)
    warnings.warn('SECRET_KEY no está en .env: se generó una temporal; las sesiones se pierden al reiniciar.')

DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Cloudflare (túnel) termina el https y avisa con X-Forwarded-Proto: así Django
# arma las URLs absolutas (logos, fondos) con https y no con http.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'giftcardbackend.aplicacionesdamasco.com,localhost,127.0.0.1')

# PIN de las cajeras para entrar a /caja (se valida en el servidor)
CAJA_PIN = os.getenv('CAJA_PIN', '')

# ============================================================
# CONEXIÓN SAP (SQL Server) — leída desde .env
# ============================================================
SAP_DB = {
    'DRIVER': os.getenv('SAP_DB_DRIVER', 'ODBC Driver 17 for SQL Server'),
    'HOST':   os.getenv('SAP_DB_HOST', ''),
    'NAME':   os.getenv('SAP_DB_NAME', ''),
    'USER':   os.getenv('SAP_DB_USER', ''),
    'PASSWORD': os.getenv('SAP_DB_PASSWORD', ''),
}

USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    # Local
    'giftcards',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================
# BASE DE DATOS — CONFIGURA AQUÍ TU CONEXIÓN
# ============================================================
# Opción 1: SQLite (default para desarrollo/pruebas)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Opción 2: SQL Server (descomentar y configurar)
# DATABASES = {
#     'default': {
#         'ENGINE': 'mssql',
#         'NAME': 'tu_base_de_datos',
#         'USER': 'tu_usuario',
#         'PASSWORD': 'tu_password',
#         'HOST': 'tu_servidor',
#         'PORT': '1433',
#         'OPTIONS': {
#             'driver': 'ODBC Driver 17 for SQL Server',
#         },
#     }
# }

# Opción 3: PostgreSQL (descomentar y configurar)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'tu_base_de_datos',
#         'USER': 'tu_usuario',
#         'PASSWORD': 'tu_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Si necesitas una segunda BD para queries (ej: SAP)
# DATABASES['sap'] = {
#     'ENGINE': 'mssql',
#     'NAME': 'SBO_DAMASCO',
#     'USER': 'sa',
#     'PASSWORD': 'tu_password',
#     'HOST': 'tu_servidor_sap',
#     'PORT': '1433',
#     'OPTIONS': {
#         'driver': 'ODBC Driver 17 for SQL Server',
#     },
# }
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS — solo el frontend del portal
from corsheaders.defaults import default_headers  # noqa: E402

CORS_ALLOWED_ORIGINS = env_list(
    'CORS_ALLOWED_ORIGINS',
    'https://giftcard.aplicacionesdamasco.com,http://localhost:6643,http://127.0.0.1:6643'
)
CORS_ALLOW_HEADERS = (*default_headers, 'x-client-token', 'x-caja-token', 'x-vendedor-token')

# Cloudflare Tunnel — dominios de producción
CSRF_TRUSTED_ORIGINS = [
    'https://giftcard.aplicacionesdamasco.com',
    'https://giftcardbackend.aplicacionesdamasco.com',
    'http://localhost:6643',
    'http://localhost:6644',
]

# DRF Config
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    # Límite de intentos de login (clientes, caja y admin) por IP
    'DEFAULT_THROTTLE_RATES': {
        'login': '10/min',
    },
}
