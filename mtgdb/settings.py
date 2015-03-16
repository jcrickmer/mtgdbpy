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
        'URL': 'http://127.0.0.1:8983/solr'
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
    },
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
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "/home/jason/projects/mtgdb/cstatic/"

STATIC_ROOT_CN = '/home/jason/projects/mtgdb/cn'
STATIC_ROOT_CARD_IMAGES = '/home/jason/projects/mtgstats/card_images'

BITLY_API_USER = 'o_l7vkb4uv0'
BITLY_API_KEY = 'R_3cbf22413b0d49b487b71db6b3b4e722'
BITLY_ACCESS_TOKEN = '9708cb7d50550b6409cd93b796990bebdde3edb0'
USE_BITLY = False
DYNAMIC_IMAGE_FILE_ROOT = '/tmp/cn_dyn_root'
