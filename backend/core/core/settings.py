import os
from pathlib import Path
from datetime import timedelta
from decouple import AutoConfig
import dj_database_url

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from multiple locations
# Priority: 1. Environment variables, 2. .env file in project root, 3. defaults
config = AutoConfig(search_path=BASE_DIR.parent)  # Look in backend/ directory for .env

# Security
SECRET_KEY = config('DJANGO_SECRET_KEY', default='your-secret-key-here')
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = [h.strip() for h in str(config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver')).split(',') if h.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'axes',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    # 'django_celery_beat',  # Commented out due to Django 5.1 compatibility issues
    
    # Local apps
    'apps.auth.apps.AuthConfig',
    'apps.preferences.apps.PreferencesConfig',
]

# Celery Configuration
# Hybrid Development Setup: Redis runs in Docker (localhost:6380), Celery runs locally
# For production, use a robust broker like RabbitMQ or a dedicated Redis instance.
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6380/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=CELERY_BROKER_URL)

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = config('CELERY_TIMEZONE', default='UTC') # Or your project's TIME_ZONE
CELERY_ENABLE_UTC = config('CELERY_ENABLE_UTC', default=True, cast=bool)
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True # Added to address deprecation warning

# MFA Cleanup Settings
UNCONFIRMED_TOTP_RETENTION_HOURS = 24 # Unconfirmed TOTP devices older than this will be deleted
USED_BACKUP_CODE_RETENTION_DAYS = 90 # Used backup codes older than this will be deleted

# Celery Beat scheduler - using built-in file-based scheduler for local development
# Note: django_celery_beat is disabled due to Django 5.1 compatibility issues
CELERY_BEAT_SCHEDULER = 'celery.beat:PersistentScheduler'

# Custom user model
AUTH_USER_MODEL = 'gradvy_auth.User'

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'core.middleware.SecurityHeadersMiddleware',  # Custom security headers
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.CookieSecurityMiddleware',  # Custom cookie security
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.SessionFingerprintMiddleware',  # Session security (after auth)
    'django_otp.middleware.OTPMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.CookieConsentMiddleware',  # Cookie consent tracking
]

ROOT_URLCONF = 'core.urls'

# Security settings
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie settings - properly configured for security
SESSION_COOKIE_SECURE = not DEBUG  # Only send over HTTPS in production
CSRF_COOKIE_SECURE = not DEBUG     # Only send over HTTPS in production
SESSION_COOKIE_HTTPONLY = True     # Prevent XSS attacks
CSRF_COOKIE_HTTPONLY = False       # CSRF needs to be accessible to JS
SESSION_COOKIE_SAMESITE = 'Lax'    # CSRF protection
CSRF_COOKIE_SAMESITE = 'Lax'       # CSRF protection
SESSION_COOKIE_AGE = 7 * 24 * 60 * 60  # 7 days session timeout
SESSION_EXPIRE_AT_BROWSER_CLOSE = False # Sessions persist across browser sessions
SESSION_SAVE_EVERY_REQUEST = True  # Update session on every request
SESSION_COOKIE_NAME = 'gradvy_sessionid'  # Custom session cookie name
CSRF_COOKIE_NAME = 'gradvy_csrftoken'     # Custom CSRF cookie name

# Additional security cookies
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
if not DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        "https://your-production-domain.com",
        "https://www.your-production-domain.com"
    ])

# CSRF & CORS
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Advanced CSRF settings
CSRF_USE_SESSIONS = False  # Use cookies instead of sessions for CSRF tokens
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# DRF Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/min',
        'user': '120/min',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration - Optimized to prevent race conditions and rapid logout
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),  # Extended to reduce refresh frequency
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),  # Longer refresh token lifetime
    'ROTATE_REFRESH_TOKENS': False,  # Disable rotation to prevent race conditions
    'BLACKLIST_AFTER_ROTATION': False,  # Disabled since rotation is off
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256', 
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    # Remove sliding token settings that can cause conflicts
}

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'two_factor:login'

# django-axes Configuration
AXES_ENABLED = True  # Re-enabled with proper exception handling
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_CALLABLE = None
AXES_VERBOSE = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Database
# Hybrid Development Setup: PostgreSQL runs in Docker (localhost:5432), Django runs locally
# Prefer a single DATABASE_URL env var (12-factor). Fallback to individual DB_* vars.
DATABASE_URL = config('DATABASE_URL', default='')
conn_max_age = config('CONN_MAX_AGE', default=600, cast=int)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=conn_max_age) # type: ignore
    }
else:
    # Individual DB settings for local development with Docker PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': config('DB_NAME', default='gradvy_db'),
            'USER': config('DB_USER', default='gradvy_user'),
            'PASSWORD': config('DB_PASSWORD', default='gradvy_secure_2024'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5433'),
        }
    }

# MongoDB Configuration
# MongoDB runs in Docker container, accessible via localhost:27017
import mongoengine

MONGODB_SETTINGS = {
    'host': config('MONGODB_URI', default='mongodb://gradvy_app:gradvy_app_secure_2024@localhost:27017/gradvy_preferences'),
    'connect': False,  # Don't connect immediately to avoid connection pool issues
    'uuidRepresentation': 'standard',
    'maxPoolSize': 20,
    'socketTimeoutMS': 20000,
    'connectTimeoutMS': 20000,
    'serverSelectionTimeoutMS': 5000,
}

# Initialize MongoDB connection
try:
    mongoengine.connect(**MONGODB_SETTINGS)
except Exception as e:
    # Log connection error but don't fail startup
    print(f"MongoDB connection warning: {e}")

# Email configuration
# Default to console backend for local development. Provide SMTP settings via env for production.
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost')

# Site ID
SITE_ID = 1

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Templates
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# MIGRATION_MODULES = {
#     'otp_totp': 'auth.migrations_otp_totp',
# }


import sys
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

