# -*- coding: utf-8 -*-

"""
Django settings for mtgdb project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from distutils.sysconfig import get_python_lib
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SITE_PACKAGES_DIR = str(get_python_lib())
DIST_PACKAGES_DIR = SITE_PACKAGES_DIR.replace('site-pack', 'dist-pack')
DEFAULT_CHARSET = 'utf-8'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fn+&ta$dafk$a57ozf9h*!@!j-&np6_ik-%tg#y=$z*@$6b^@$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

ALLOWED_HOSTS = ['127.0.0.1', 'smoker', '192.168.0.7', 'venser', 'localhost']
INTERNAL_IPS = (
    '127.0.0.1',
    '0.0.0.0',
    'localhost',
    '192.168.0.2',
    '192.168.0.3',
    '192.168.0.4',
    '192.168.0.5',
    '192.168.0.6',
    '192.168.0.7',
    '192.168.0.8',
    '192.168.0.9',
    '192.168.0.10',
    '192.168.0.11',
    '192.168.0.12',
    '192.168.0.13',
    '192.168.0.14',
    '192.168.0.15',
    '192.168.0.16',
    '192.168.0.17',
    '192.168.0.18',
    '192.168.0.19',
    '192.168.0.20',
    'smoker')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'django_nose',
    'ajax_select',
    'mathfilters',
    'content',
    'cards',
    'decks',
]

MIDDLEWARE = (
    #    'cards.stats_middleware.StatsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'tz_detect.middleware.TimezoneMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cards.deckbox_middleware.DeckboxMiddleware',
)

ROOT_URLCONF = 'mtgdb.urls'

WSGI_APPLICATION = 'mtgdb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mtgdb2',
                'USER': 'root',
                'PASSWORD': 'godzilla'
    },
}

# define the lookup channels in use on the Admin for type-ahead autocomplete
AJAX_LOOKUP_CHANNELS = {
    #  simple: search Person.objects.filter(name__icontains=q)
    # 'deckcard'  : {'model': 'cards.PhysicalCard', 'search_field': 'id'},
    'deckcard': ('cards.lookups', 'PhysicalCardLookup'),
    'physicalcard': ('cards.lookups', 'PhysicalCardLookup'),
    'expansionset': ('cards.lookups', 'ExpansionSetLookup'),
    'card': ('cards.lookups', 'CardLookup'),
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'content', 'templates'),
                 os.path.join(BASE_DIR, 'cards', 'templates'),
                 os.path.join(BASE_DIR, 'decks', 'templates'),
                 os.path.join(BASE_DIR, 'mtgdb', 'templates'),
                 os.path.join(SITE_PACKAGES_DIR, 'django', 'contrib', 'admin', 'templates'),
                 os.path.join(SITE_PACKAGES_DIR, 'ajax_select', 'templates'),
                 os.path.join(DIST_PACKAGES_DIR, 'django', 'contrib', 'admin', 'templates'),
                 os.path.join(DIST_PACKAGES_DIR, 'ajax_select', 'templates'),
                 ],
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        }
    }
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        # 'file': {
        #    'level': 'DEBUG',
        #    'class': 'logging.FileHandler',
        #    'filename': '/tmp/debug.log',
        # },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            # 'formatter': 'simple'
        },
    },
    'loggers': {
        'cards.admin': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'cards.views': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'cards.models': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'cards': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'decks.models': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
CARDS_SEARCH_CACHE_TIME = 60 * 15

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "/home/jason/projects/mtgdb2/cstatic/"

STATIC_ROOT_CN = '/home/jason/projects/mtgdb2/cn'
STATIC_ROOT_CARD_IMAGES = '/home/jason/projects/mtgstats/card_images'

DYNAMIC_IMAGE_FILE_ROOT = '/tmp/cn_dyn_root'

# Bit.ly
BITLY_API_USER = 'XXXXXXXX'
BITLY_API_KEY = 'XXXXXXXX'
BITLY_ACCESS_TOKEN = 'XXXXXXXX'
USE_BITLY = False


# Twitter
# for dev327364652
APP_KEY = 'XXXXXXXX'
APP_SECRET = 'XXXXXXXX'
OAUTH_TOKEN = 'XXXXXXXX'
OAUTH_TOKEN_SECRET = 'XXXXXXXX'

BETTER_BATTLE_PATH = '/home/jason/projects/mtgdb2'

HOME_URL = 'http://mtgcardtech.jcrickmer.com/'
DECKBOX_LOGIN_URL = 'https://mtgcardtech.jcrickmer.com/store/custLogin.pl'
DECKBOX_URL = 'https://mtgcardtech.jcrickmer.com/store/custCheckout.pl'
DECKBOX_SESSION_COOKIE_KEY = 'PGCUSTISA'
DECKBOX_ORDER_COOKIE_KEY = 'ORDERIDISA'
DECKBOX_PRICE_URL_BASE = "/cards/_cardpricedbtest/"
DECKBOX_AUTH_SECRET = "patsgamesRocks"

# Google Analytics
GA_TRACKING_ID = 'UA-51777211-2'
GTM_ID = 'GTM-WN9L8RJ'

ELASTICSEARCH_HOST = 'localhost'
ELASTICSEARCH_PORT = 9200

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_TASK_TRACK_STARTED = True
