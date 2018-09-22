# -*- coding: utf-8 -*-

from settings import *

DEFAULT_CHARSET = 'utf-8'

DEBUG = TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '172-31-44-78', 'ip-172-31-47-162', '172.31.47.162', 'spellbook.patsgames.com', '34.215.208.197']
INTERNAL_IPS = ()
#DATABASE_NAME = 'production'
#DATABASE_USER = 'app'
#DATABASE_PASSWORD = 'letmein'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mtgdb',
        'USER': 'root',
        'PASSWORD': 'godzilla'
    },
}
HAYSTACK_CONNECTIONS['default']['URL'] = 'http://127.0.0.1:8983/solr/mtgdb'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        #'file': {
        #    'level': 'DEBUG',
        #    'class': 'logging.FileHandler',
        #    'filename': '/tmp/debug.log',
        #},
        #'applogfile': {
        #    'level': 'DEBUG',
        #    'class': 'logging.handlers.RotatingFileHandler',
        #    'filename': os.path.join('/tmp/', 'mtgdb_debug.log'),
        #    'maxBytes': 1024 * 1024 * 15,  # 15MB
        #    'backupCount': 10,
        #},
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
            'level': 'INFO',
            'propagate': True,
        },
        'APPNAME': {
            'handlers': ['console', ],
            'level': 'INFO',
        },
    },
}

STATIC_ROOT_CN = '/opt/mtgdb-prod/cn'
STATIC_ROOT_CARD_IMAGES = '/var/mtgdb/card_images'
DYNAMIC_IMAGE_FILE_ROOT = '/var/mtgdb/cn_dyn_root'

USE_BITLY = True

# Twitter
# for card_ninja (production)
OAUTH_TOKEN = 'XXXXX'
OAUTH_TOKEN_SECRET = 'XXXXX'

BETTER_BATTLE_PATH = '/opt/mtgdb-prod'

HOME_URL = 'https://www.patsgames.com/'
DECKBOX_LOGIN_URL = 'https://www.patsgames.com/store/custLogin.pl'
DECKBOX_URL = 'https://www.patsgames.com/store/custCheckout.pl'
DECKBOX_SESSION_COOKIE_KEY = 'PGCUSTISA'
DECKBOX_ORDER_COOKIE_KEY = 'ORDERIDISA'
DECKBOX_PRICE_URL_BASE = 'https://www.patsgames.com/store/getCardInfo.pl?mvid='
DECKBOX_AUTH_SECRET = "patsgamesRocks"

# Google Analytics
GA_TRACKING_ID = 'UA-112384301-1'
GTM_ID = 'GTM-TFQMBXJ'

ELASTICSEARCH_HOST = 'vpc-spellbook-u24glnd5zfp4imkyavrokeygku.us-west-2.es.amazonaws.com'
ELASTICSEARCH_PORT = 80
