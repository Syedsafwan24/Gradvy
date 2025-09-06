"""
Development settings for Gradvy project.

These settings are used during local development and testing.
"""

from .base import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database - Hybrid setup with Docker PostgreSQL
DATABASES = {
    'default': dj_database_url.parse(
        config(
            'DATABASE_URL',
            default='postgresql://gradvy_user:gradvy_password@localhost:5432/gradvy_db'
        )
    )
}

# Celery Configuration - Hybrid setup with Docker Redis
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6380/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=CELERY_BROKER_URL)

# Development-specific middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
] + MIDDLEWARE

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# CSRF settings for development
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Cookie settings for development (less secure for easier development)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

# Security settings (relaxed for development)
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Email backend for development (console backend)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django REST Framework - Development settings
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Adds browsable API for development
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/min',  # More lenient for development
        'user': '500/min',
    },
})

# JWT settings for development (longer tokens for easier testing)
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),  # Longer for development
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
})

# Axes settings for development (more lenient)
AXES_FAILURE_LIMIT = 10  # Allow more attempts in development
AXES_COOLOFF_TIME = timedelta(minutes=5)  # Shorter lockout

# Development-specific logging
LOGGING['handlers'].update({
    'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',  # More verbose in development
    },
})

LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps.auth']['level'] = 'DEBUG'

# Django Debug Toolbar (optional - uncomment to enable)
# if DEBUG:
#     INSTALLED_APPS += ['debug_toolbar']
#     MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
#     INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Cache configuration for development (dummy cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# File storage for development
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Static files configuration for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Create logs directory if it doesn't exist
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)