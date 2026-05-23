import os
from pathlib import Path

# ============================================================================
# CONFIGURATION DE BASE
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-gemba-lean-2024'

DEBUG = True

# Ajoutez ngrok URL ici quand vous lancez ngrok
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.ngrok.io']

# ============================================================================
# APPLICATIONS INSTALLÉES
# ============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'salle',  # Notre application principale
]

# ============================================================================
# MIDDLEWARE
# ============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================================
# URLS ET TEMPLATES
# ============================================================================

ROOT_URLCONF = 'GEMBA_LEAN.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'GEMBA_LEAN.wsgi.application'

# ============================================================================
# BASE DE DONNÉES
# ============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================================================
# VALIDATION DES MOTS DE PASSE
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================================
# INTERNATIONALISATION
# ============================================================================

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Casablanca'
USE_I18N = True
USE_TZ = True

# ============================================================================
# FICHIERS STATIQUES ET MÉDIAS
# ============================================================================

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# PARAMÈTRES PAR DÉFAUT
# ============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# ============================================================================
# ==================== CONFIGURATION DES EMAILS ====================
# ============================================================================

# Pour le développement avec ngrok (liens cliquables sur mobile)
# Utilisez la console pour tester (recommandé)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuration Gmail pour l'envoi d'emails en production (Décommentez pour production)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'hinimdoumorsia@gmail.com'
# EMAIL_HOST_PASSWORD = 'iotv nfva vpio xiad'
# DEFAULT_FROM_EMAIL = 'GEMBA LEAN <hinimdoumorsia@gmail.com>'

# Paramètres supplémentaires SMTP
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 30

# ============================================================================
# URL DU SITE (pour les liens dans les emails)
# ============================================================================

# Pour le développement avec ngrok - mettez à jour cette URL quand vous lancez ngrok
# Exemple: SITE_URL = 'https://abc123.ngrok.io'
SITE_URL = 'http://127.0.0.1:8000'

# Pour récupérer dynamiquement l'URL (plus flexible)
def get_current_site_url(request=None):
    """Retourne l'URL du site dynamiquement"""
    if request:
        return f"http://{request.get_host()}"
    return SITE_URL

# ============================================================================
# DÉLAI D'EXPIRATION DU TOKEN DE VÉRIFICATION (en heures)
# ============================================================================

VERIFICATION_TOKEN_EXPIRY_HOURS = 24

# ============================================================================
# ==================== CONFIGURATION DU LOGGING ====================
# ============================================================================

# Création automatique du dossier logs s'il n'existe pas
LOGS_DIR = BASE_DIR / 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(LOGS_DIR / 'email.log'),
            'mode': 'a',
            'encoding': 'utf-8',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'salle.utils': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}