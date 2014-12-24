import os
import sys

sys.path.append('/opt/mtgdbpy')

os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'mtgdbpy.settings_prod'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
