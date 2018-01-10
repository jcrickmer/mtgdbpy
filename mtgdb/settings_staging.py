# -*- coding: utf-8 -*-

from settings import *

DEFAULT_CHARSET = 'utf-8'

DEBUG = TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'card.ninja', '172-31-44-78', 'ip-172-31-47-162', '172.31.47.162', 'staging.magiccards.tech','34.215.208.197']
INTERNAL_IPS = ()
#DATABASE_NAME = 'production'
#DATABASE_USER = 'app'
#DATABASE_PASSWORD = 'letmein'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mtgdb_staging',
        'USER': 'root',
        'PASSWORD': 'godzilla'
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/mtgdb_staging',
        'INCLUDE_SPELLING': True,
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/debug.log',
        },
        'applogfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('/tmp/', 'mtgdb_debug.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            #'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'cards.views': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'APPNAME': {
            'handlers': ['console', ],
            'level': 'DEBUG',
        },
    },
}
TEMPLATES[0]['DIRS'].append(os.path.join('/opt/mtgdb-staging_env/lib/python2.7/site-packages/django/contrib', 'admin', 'templates'))
TEMPLATES[0]['DIRS'].append('/opt/mtgdb-staging_env/lib/python2.7/site-packages/django/contrib/admin/templates')
TEMPLATES[0]['DIRS'].append('/opt/mtgdb-staging_env/lib/python2.7/site-packages/haystack/templates')
TEMPLATES[0]['DIRS'].append('/opt/mtgdb-staging_env/lib/python2.7/site-packages/ajax_select/templates')

STATIC_ROOT = "/opt/mtgdb-staging_env/lib/python2.7/site-packages/django/contrib/admin/static"
STATIC_ROOT_CN = '/opt/mtgdb-staging/cn'
STATIC_ROOT_CARD_IMAGES = '/var/mtgdb/card_images'
DYNAMIC_IMAGE_FILE_ROOT = '/var/mtgdb/cn_dyn_root'

USE_BITLY = True

# Twitter
# for card_ninja (production)
OAUTH_TOKEN = 'XXXXX'
OAUTH_TOKEN_SECRET = 'XXXXX'

BETTER_BATTLE_PATH = '/opt/mtgdb-staging'
