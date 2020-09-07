"""
Django settings for clustr project.
Generated by 'django-admin startproject' using Django 3.0.6.
For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import environ
import django_heroku
import dj_database_url

DEV = True #false for production, else True for dev

# from django.utils.translation import gettext as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#env variables init
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
env_file = os.path.join(BASE_DIR, ".env")
environ.Env.read_env(env_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = ['cluster-mvp.herokuapp.com', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.sites',
    'customers',
    'kitchen',
    'restaurant_admin',
    'shift_admin',
    'crispy_forms',
    'storages',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'stripe',
    'django_extensions',
    'phonenumber_field',
    'comms',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'cashier',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'clustr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': '',
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

WSGI_APPLICATION = 'clustr.wsgi.application'

# Activate Django-Heroku.
django_heroku.settings(locals())

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
if DEV:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
              'NAME': env('DB_NAME'),
              'USER': env('DB_USER'),
              'PASSWORD': env("DB_PASS"),
              'HOST': env('DB_HOST'),   # Or an IP Address that your DB is hosted on
              'PORT': '',
        }
     }
else:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/


LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'es-mx'


TIME_ZONE = 'America/Mexico_City'
USE_TZ = True

USE_I18N = True

USE_L10N = True

USE_TZ = True
#
LANGUAGES = [
    ('en-us','English'),
    ('es-MX', 'Spanish')
]


#Stripe Settings
STRIPE_PUBLISHABLE_KEY = env('STRIPE_API_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')

#twilio settings
TWILIO_SID = env('TWILIO_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
LOGIN_REDIRECT_URL = 'restaurant_admin/my_menus'
LOGOUT_REDIRECT_URL = 'restaurant_admin/logout_view'
#AWS stuff
STATIC_URL = 'https://s3.console.aws.amazon.com/s3/buckets/cluster-dev-bucket/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
#AWS stuff
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')

AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')

AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')


AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend',
                           'cashier.auth_backend.PasswordlessAuthBackend',
                           'allauth.account.auth_backends.AuthenticationBackend']

#Email Configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = "clustrfood@gmail.com"
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

SITE_ID = 10

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
