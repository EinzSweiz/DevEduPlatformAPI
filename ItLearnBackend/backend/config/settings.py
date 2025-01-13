from pathlib import Path
from decouple import config
import watchtower
import boto3
from datetime import timedelta
import os
from datetime import datetime
import sys
import logging

logger = logging.Logger(__name__)

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
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'web']


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
    'django_prometheus',

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
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # External middleware
    'allauth.account.middleware.AccountMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# ==========================
# CORS and CSRF
# ==========================

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.wsgi.application'
WEBSITE_URL = 'http://127.0.0.1:8015'
FRONTEND_URL = 'http://localhost:3000'
CORS_ALLOW_CREDENTIALS=True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:8015',
]
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8015', 
    'http://localhost:3000',

]
CORS_ORIGINS_WHITELIST = [
    'http://127.0.0.1:8015', 
    'http://localhost:3000',

]


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


# ==========================
# DATABASE
# ==========================

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

# ==========================
# CELERY
# ==========================
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', cast=str, default='django-db')
CELERY_BROKER_URL = config('CELERY_BROKER_URL', cast=str, default='kafka://localhost:9092')
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_BEAT_SCHEDULER_MAX_INTERVAL = 60

broker_transport_options = {
    'retry_on_timeout': True,
    'max_retries': 5,
    'interval_start': 0,   # Start retry delay immediately
    'interval_step': 0.2,  # Step-up delay between retries
    'interval_max': 0.5,   # Maximum delay between retries
}
CELERY_WORKER_CONCURRENCY = 4  # Limit the number of concurrent worker threads (adjust as needed)

# Soft and hard task time limits
CELERY_TASK_SOFT_TIME_LIMIT = 300  # Abort task gracefully after 5 minutes
CELERY_TASK_TIME_LIMIT = 360  # Hard limit of 6 minutes

# Prefetch multiplier to control the number of tasks a worker prefetches
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Prevent worker from prefetching too many tasks

CELERY_TASK_IGNORE_RESULT = True  # Set to True if results are not needed


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
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",  # For media files
        "LOCATION": "media/",  # Ensure this matches your MEDIA_ROOT
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",  # For static files
    },
}

#=========================
# AWS LOGS
#=========================

logger = logging.getLogger('default')  # Use 'default' logger explicitly
logger_boto3_client = boto3.client(
    'logs',
    aws_access_key_id=config('AWS_ACCESS_KEY', cast=str, default=None),
    aws_secret_access_key=config('AWS_SECRET_KEY', cast=str, default=None),
    region_name='us-east-1'
)
CLOUDWATCH_DEFAULT_LOG_STREAM_NAME = f"app-log-stream-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'default': {
#             'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         },
#     },
#     'handlers': {
#         'file': {
#             'level': 'INFO',
#             'class': 'logging.FileHandler',
#             'filename': '/usr/src/backend/logs/coursesapp.log',
#             'formatter': 'default',
#         },
#         'cloudwatch': {
#             'level': 'INFO',  # Send only INFO and above to CloudWatch
#             'class': 'watchtower.CloudWatchLogHandler',
#             'boto3_client': logger_boto3_client,
#             'log_group': '/courses-it-logs-group',
#             'stream_name': 'manual-test-log-stream',
#             'formatter': 'default',
#             'send_interval': 0,
#         },
#         'console': {
#             'level': 'INFO',  # Show only warnings and above in the console
#             'class': 'logging.StreamHandler',
#             'formatter': 'default',
#         },
#     },
#     'loggers': {
#         'default': {
#             'handlers': ['file', 'cloudwatch', 'console'],  # Log to all handlers
#             'level': 'INFO',
#             'propagate': False,
#         },
#         'django': {
#             'handlers': ['file', 'cloudwatch', 'console'],
#             'level': 'INFO',
#             'propagate': False,
#         },
#         'botocore': {
#             'handlers': ['file'],
#             'level': 'WARNING',
#             'propagate': False,
#         },
#     },
# }
logging.getLogger('default').info('This is a test error log for CloudWatch!')

#=====================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
