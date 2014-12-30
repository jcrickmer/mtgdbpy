from settings import *

DEBUG = TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'card.ninja', '172-31-44-78']
INTERNAL_IPS = ()
#DATABASE_NAME = 'production'
#DATABASE_USER = 'app'
#DATABASE_PASSWORD = 'letmein'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mtgdbpy',
        'USER': 'root',
        'PASSWORD': 'godzilla'
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        #'file': {
        #    'level': 'DEBUG',
        #    'class': 'logging.FileHandler',
        #    'filename': '/tmp/debug.log',
        #},
        'applogfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('/tmp/', 'mtgdbpy_debug.log'),
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
        'mtgdbapp.views': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'APPNAME': {
            'handlers': ['applogfile', ],
            'level': 'DEBUG',
        },
    },
}

STATIC_ROOT = "/opt/mtgdbpy/cstatic/"
