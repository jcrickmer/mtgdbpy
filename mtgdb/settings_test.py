# -*- coding: utf-8 -*-

from settings import *

DEFAULT_CHARSET='utf-8'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mtgdb',
        'USER': 'root',
        'PASSWORD': 'tester',
        'HOST': '127.0.0.1',
        'PORT': '13006',
        'SOCKET': '/tmp/testramdisk/mysql.sock',
    },
}