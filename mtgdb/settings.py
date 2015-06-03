"""
Django settings for mtgdb project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fn+&ta$dafk$a57ozf9h*!@!j-&np6_ik-%tg#y=$z*@$6b^@$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

ALLOWED_HOSTS = []
INTERNAL_IPS = (
    '127.0.0.1',
    'localhost',
    '192.168.1.6',
    '192.168.1.7',
    '192.168.1.8',
    '192.168.1.11',
    '192.168.1.18',
    '192.168.1.19',
    'smoker')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_nose',
    'ajax_select',
    'mathfilters',
    'haystack',
    'cards',
    'decks',
    'rules',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mtgdb.urls'

WSGI_APPLICATION = 'mtgdb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mtgdbpy',
                'USER': 'mtgdb',
                'PASSWORD': 'password'
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr',
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
        # NOTE: when turning this on for the first time, a "rebuild_index" is
        # required. Then, poked the solr instance directly to get it started with
        # curl
        # 'http://localhost:8983/solr/select?q=brimaz&spellcheck=true&spellcheck.collate=true&spellcheck.build=true'
        # Unfortuantely, it didn't work. :(
        'INCLUDE_SPELLING': True,
    },
}

# define the lookup channels in use on the Admin for type-ahead autocomplete
AJAX_LOOKUP_CHANNELS = {
    #  simple: search Person.objects.filter(name__icontains=q)
    #'deckcard'  : {'model': 'cards.PhysicalCard', 'search_field': 'id'},
    'deckcard': ('cards.lookups', 'PhysicalCardLookup'),
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'cards', 'templates'),
    os.path.join(BASE_DIR, 'decks', 'templates'),
    os.path.join(BASE_DIR, 'rules', 'templates'),
    os.path.join(BASE_DIR, 'mtgdb', 'templates'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        #'file': {
        #    'level': 'DEBUG',
        #    'class': 'logging.FileHandler',
        #    'filename': '/tmp/debug.log',
        #},
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            #'formatter': 'simple'
        },
    },
    'loggers': {
        'cards.views': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'cards.models': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'decks.models': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "/home/jason/projects/mtgdb/cstatic/"

STATIC_ROOT_CN = '/home/jason/projects/mtgdb/cn'
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
