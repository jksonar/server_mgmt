"""
Django settings for server_mgmt project.

Generated by 'django-admin startproject' using Django 5.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-yv!h0svrl8(=9&sl#*@4gn@al(df4g7ln$&k579h@7ayz9#*s!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    'accounts',
    'django_celery_beat',
    'django_celery_results',
    'auditlog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
]

ROOT_URLCONF = 'server_mgmt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'templates') ], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'server_mgmt.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'accounts.User'

# Celery Configuration
# Using filesystem as broker and result backend
CELERY_BROKER_URL = 'filesystem://'
CELERY_RESULT_BACKEND = 'file://{}/.celery/results'.format(BASE_DIR)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Filesystem broker settings
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'data_folder_in': os.path.join(BASE_DIR, '.celery/broker/in'),
    'data_folder_out': os.path.join(BASE_DIR, '.celery/broker/out'),
    'data_folder_processed': os.path.join(BASE_DIR, '.celery/broker/processed'),
}

# Create necessary directories
os.makedirs(os.path.join(BASE_DIR, '.celery/results'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, '.celery/broker/in'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, '.celery/broker/out'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, '.celery/broker/processed'), exist_ok=True)

# Import Celery Beat schedule
from core.celery_beat_schedule import BEAT_SCHEDULE
CELERY_BEAT_SCHEDULE = BEAT_SCHEDULE

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development
EMAIL_HOST = 'smtp.example.com'  # Change in production
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'  # Change in production
EMAIL_HOST_PASSWORD = 'your-password'  # Change in production
DEFAULT_FROM_EMAIL = 'Server Management <noreply@servermgmt.example.com>'

# SSL Certificate settings
SSL_NOTIFICATION_DAYS = [30, 14, 7, 3, 1]  # Days before expiry to send notifications

CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]

CRISPY_TEMPLATE_PACK = "bootstrap5"
