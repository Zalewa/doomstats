"""
Django settings for doomstats project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import json
import errno

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

default_cfg = {
    "secret_key": 'aha*7=pe^q8xwrrnioprr287vxmh1dkku&f1dtasqvp3)4^**j',
    "timezone": "UTC",
    "static_url": "/static/",
    "databases" : {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
}


def get_cfg():
    paths = [
        os.path.join(BASE_DIR, "config.json"),
        "/etc/doomstats/config.json"
    ]
    paths = filter(lambda p: os.path.isfile(p), paths)
    if not paths:
        if DEBUG:
            print >>sys.stderr, \
                "Using default config due to missing " \
                "config.json and DEBUG = {0}".format(DEBUG)
            return default_cfg
        else:
            raise IOError('no config.json file found')
    cfgpath = paths[0]
    print >>sys.stderr, "Using config at '{0}'".format(cfgpath)
    with open(cfgpath, "rb") as f:
        custom_cfg = json.loads(f.read())
        if not DEBUG and 'secret_key' not in custom_cfg:
            raise ValueError("no 'secret_key' in config")
        combined = {}
        combined.update(default_cfg)
        combined.update(custom_cfg)
        return combined


cfg = get_cfg()


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = cfg["secret_key"]


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stats',
    'googlecharts',
    'presentation'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'doomstats.urls'

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
                'stats.views.load_site_global_context'
            ],
        },
    },
]

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

WSGI_APPLICATION = 'doomstats.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = cfg["databases"]


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = cfg["timezone"]

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = cfg["static_url"]
