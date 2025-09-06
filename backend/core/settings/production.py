"""
Production settings for Gradvy project.

These settings are optimized for production deployment with security and performance in mind.
"""

from .base import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Production hosts - must be configured properly
ALLOWED_HOSTS = [h.strip() for h in str(config('DJANGO_ALLOWED_HOSTS', default='')).split(',') if h.strip()]

# Database - Production database URL
DATABASES = {
    'default': dj_database_url.parse(
        config(
            'DATABASE_URL',
            # No default for production - must be explicitly configured
        )
    )
}

# Celery Configuration - Production Redis/RabbitMQ
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=CELERY_BROKER_URL)

# Additional Celery settings for production
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_WORKER_CONCURRENCY = config('CELERY_WORKER_CONCURRENCY', default=4, cast=int)
CELERY_WORKER_MAX_TASKS_PER_CHILD = 50
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_TIME_LIMIT = 600  # 10 minutes

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie settings for production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SAMESITE = 'Strict'

# CORS settings for production (restrictive)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in str(config('CORS_ALLOWED_ORIGINS', default='')).split(',') if origin.strip()
]

# CSRF settings for production
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in str(config('CSRF_TRUSTED_ORIGINS', default='')).split(',') if origin.strip()
]

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@gradvy.com')

# Django REST Framework - Production settings
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        # Browsable API disabled in production for security
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/min',  # Strict rate limiting in production
        'user': '60/min',
    },
})

# JWT settings for production (shorter tokens for security)
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),
})

# Axes settings for production (strict)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_ENABLE_ADMIN = False  # Don't show axes in admin for security

# Cache configuration for production (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('CACHE_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'gradvy',
        'TIMEOUT': 300,
    }
}

# Session configuration for production
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600  # 1 hour

# File storage for production (use cloud storage like S3)
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
# AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')

# Static files configuration for production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Production logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/gradvy/gradvy.log',
            'maxBytes': 1024 * 1024 * 100,  # 100MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/gradvy/error.log',
            'maxBytes': 1024 * 1024 * 100,  # 100MB
            'backupCount': 10,
            'formatter': 'json',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.auth': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'error_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Additional production security measures
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Database connection pooling for production
DATABASES['default'].update({
    'CONN_MAX_AGE': 60,
    'OPTIONS': {
        'MAX_CONNS': 20,
        'MIN_CONNS': 5,
    }
})

# Monitoring and health checks
INSTALLED_APPS += [
    # Add monitoring apps like django-health-check, sentry, etc.
    # 'health_check',
    # 'health_check.db',
    # 'health_check.cache',
]

# Sentry configuration for error tracking (optional)
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
# from sentry_sdk.integrations.celery import CeleryIntegration

# sentry_sdk.init(
#     dsn=config('SENTRY_DSN', default=''),
#     integrations=[
#         DjangoIntegration(auto_enabling=True),
#         CeleryIntegration(auto_enabling=True),
#     ],
#     traces_sample_rate=0.1,
#     send_default_pii=False,
#     environment=config('SENTRY_ENVIRONMENT', default='production'),
# )