from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtgdb.settings')

# Celery currently requires Redis! Be sure to install and start the Redis service...
#
#     sudo yum install redis
#     sudo service redis start
#     sudo service redis status
#

# REVISIT - This is currently hard-coded instead of configured. Should be ok for now, but something that we should
# come back and revisit.
app = Celery('asyncsrvc', broker="redis://127.0.0.1:6379/")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    ''' Simple debug task that dumps the request information to the Celery console/log.'''
    print('Request: {0!r}'.format(self.request))


from time import sleep


@app.task(bind=True)
def sleep_task(self):
    ''' Simple debug task that takes 14 seconds to complete. Progress is dumped to the Celery console/log.'''
    print('sleep_task: Request: {0!r}'.format(self.request))
    for second in range(0, 14):
        print("sleep_task second {}".format(second))
        sleep(1)
    print('sleep_task: complete!')
