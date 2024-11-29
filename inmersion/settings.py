"""
Django settings for inmersion project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
import os


load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure--o%d-5g$i*uruzs2q^)!32)gudg4puyn2rve4#d7ke32fc1^!q')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['https://inmersion-production.up.railway.app/']

AUTH_USER_MODEL = 'core.Usuario'

CSRF_TRUSTED_ORIGINS = ['https://inmersion-production.up.railway.app']

# Application definition

INSTALLED_APPS = [
    'daphne',
    'channels',
    'crispy_forms',
    'crispy_bootstrap5',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'core',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inmersion.urls'

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

#WSGI_APPLICATION = 'inmersion.wsgi.application'

ASGI_APPLICATION = 'inmersion.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [
                {
                    "host": os.getenv("REDISHOST", "redis.railway.internal"),
                    "port": int(os.getenv("REDISPORT", 6379)),
                    "password": os.getenv("REDISPASSWORD", 'XoCOAhIgrEPJApBwphXLceTXCoCgZmUb'), 
                },
            ],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

#DATABASES = {
  #  'default': {
 #       'ENGINE': 'postgresql://postgres:tIFdNRdzPHsNDSNREdFDKcvWfysJmUUF@autorack.proxy.rlwy.net:55372/railway',
#        'NAME': 'prueba',
        #'USER': 'postgres',
       # 'PASSWORD': 'admin',
      #  'HOST': 'localhost',  # O la dirección del servidor
     #   'PORT': '5432',       # O el puerto que estés utilizando
    #    'OPTIONS': {
   #         'client_encoding': 'utf8',  # Asegúrate de usar utf8
  #      },
 #   }
#}

print("DATABASE_URL:", os.getenv("DATABASE_URL"))

DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'core/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_DIRS = [
    BASE_DIR / "core/static", 
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

#VARIABLE DE REDIRECCION DE LOGIN Y LOGOUT
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"