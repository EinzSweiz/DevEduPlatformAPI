from pathlib import Path
from decouple import config
import watchtower
from datetime import timedelta
import os
import sys

sys.path.append(config("PYTHONPATH"))

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================
# EMAIL CONFIGURATION
# ==========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', cast=str, default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', cast=str, default='587')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool, default=False)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', cast=str, default=None)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', cast=str, default=None)
DEFAULT_FROM_EMAIL = config('ADMIN_USER_EMAIL', cast=str, default=None)
ADMIN_USER_NAME = config('ADMIN_USER_NAME', cast=str, default='Admin User')
ADMIN_USER_EMAIL = config('ADMIN_USER_EMAIL', cast=str, default=None)

ADMINS = []
MANAGERS = []
if all([ADMIN_USER_NAME, ADMIN_USER_EMAIL]):
    ADMINS.append((ADMIN_USER_NAME, ADMIN_USER_EMAIL))
    MANAGERS = ADMINS


# ==========================
# SECURITY
# ==========================
SECRET_KEY = config('SECRET_KEY', cast=str, default=None)
DEBUG = config('DEBUG', cast=bool, default=False)
ALLOWED_HOSTS = ['localhost', '127.0.0.1',]

# ==========================
# INSTALLED APPS
# ==========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

     # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'dj_rest_auth.registration',
    'django_celery_beat',
    'django_celery_results',
    'channels',
    'drf_yasg',

    #custom apps
    'useraccounts'
]

# ==========================
# AUTHENTICATION AND JWT
# ==========================
AUTH_USER_MODEL = 'useraccounts.User'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_SIGNUP_EMAIL_VERIFICATION = False
SOCIALACCOUNT_EMAIL_REQUIRED = False

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "SIGNING_KEY": 'acomplexkey',
    "ALGORITHM": "HS512",
}

# ==========================
# DJANGO REST
# ==========================
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False,
    # 'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    # 'REFRESH_TOKEN_LIFETIME': timedelta(days=3)
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        'rest_framework_simplejwt.authentication.JWTAuthentication',    
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/day',
        'anon': '100/hour',
        'login': '10/minute',
    },
}


# =======================
#        DOMAINS
# =======================


# ==========================
# MIDDLEWARE
# ==========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # External middleware
    'allauth.account.middleware.AccountMiddleware',
]

# ==========================
# CORS and CSRF
# ==========================

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.wsgi.application'
WEBSITE_URL = ' http://127.0.0.1:8013/'

# =======================
# DJANGO TEMPLATES
# =======================

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


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Default database settings
DATABASES = {}

# Use SQLite for tests
if 'pytest' in sys.argv[0]:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
# Use SQLite for local development (DEBUG = True)
elif config('DEBUG', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
# Use PostgreSQL for production (DEBUG = False)
else:
    DATABASES = {
        'default': {
            'ENGINE': config('SQL_ENGINE', default='django.db.backends.postgresql'),
            'NAME': config('SQL_DATABASE', default=''),
            'USER': config('SQL_USER', default=''),
            'PASSWORD': config('SQL_PASSWORD', default=''),
            'HOST': config('SQL_HOST', default=''),
            'PORT': config('SQL_PORT', default=''),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==========================
# STATIC AND MEDIA FILES
# ==========================
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


#=====================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
