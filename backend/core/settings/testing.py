"""
Testing settings for Gradvy project.

These settings are optimized for running tests with speed and isolation in mind.
"""

from .base import *

# Test database settings
DEBUG = False
TESTING = True

# Use SQLite for faster tests (or keep PostgreSQL if needed for specific tests)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory database for fastest tests
        'TEST': {
            'NAME': ':memory:',
        },
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Password hashers - use fast hasher for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Fast but insecure - only for tests
]

# Celery settings for testing (eager execution)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

# Cache configuration for testing (dummy cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Media files for testing (in memory)
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# Static files for testing (simplified)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Session configuration for testing
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Security settings (relaxed for testing)
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# CORS settings for testing
CORS_ALLOW_ALL_ORIGINS = True

# Django REST Framework - Testing settings
REST_FRAMEWORK.update({
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/min',  # No throttling in tests
        'user': '1000/min',
    },
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
})

# JWT settings for testing (longer tokens to avoid expiry during tests)
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
})

# Axes settings for testing (disabled or very lenient)
AXES_ENABLED = False  # Disable axes in tests to avoid lockouts

# Logging configuration for testing (minimal logging)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'root': {
        'handlers': ['null'],
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': 'ERROR',  # Only log errors in tests
            'propagate': False,
        },
        'apps.auth': {
            'handlers': ['null'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Test-specific settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# MFA cleanup settings for testing (short retention for faster test cleanup)
UNCONFIRMED_TOTP_RETENTION_HOURS = 1
USED_BACKUP_CODE_RETENTION_DAYS = 1

# Disable some middleware for faster tests
MIDDLEWARE = [
    middleware for middleware in MIDDLEWARE
    if middleware not in [
        'axes.middleware.AxesMiddleware',  # Disable axes in tests
        'corsheaders.middleware.CorsMiddleware',  # Not needed in tests
    ]
]

# Time zone for testing
USE_TZ = True
TIME_ZONE = 'UTC'

# Template settings for testing (minimal)
TEMPLATES[0]['OPTIONS']['debug'] = False

# Remove some apps not needed for testing
INSTALLED_APPS = [
    app for app in INSTALLED_APPS
    if app not in [
        'axes',  # Not needed in tests
        'corsheaders',  # Not needed in tests
    ]
]

# Test-specific constants
TEST_USER_EMAIL = 'test@example.com'
TEST_USER_PASSWORD = 'testpassword123'
TEST_SUPERUSER_EMAIL = 'admin@example.com'
TEST_SUPERUSER_PASSWORD = 'adminpassword123'