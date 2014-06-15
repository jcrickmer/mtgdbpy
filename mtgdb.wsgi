import os
import sys

sys.path.append('/home/jason/projects/mtgdbpy')

os.environ['PYTHON_EGG_CACHE'] = '/home/jason/projects/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'mtgdbpy.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
