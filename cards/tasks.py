# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from asyncsrvc.celery import app as asyncsrvc
from cards.models import Format

import logging

logger = logging.getLogger(__name__)


@asyncsrvc.task(bind=True)
def populate_format_cards(self, format_pk):
    ''' For a given format pk, call the format's populate_format_cards method. Note that this is DESTRUCTIVE at the
        current time. This may be need to be improved upon in the future.

        This method is meant to be invoked as an asynchronous task with Celery.
        '''
    format = Format.objects.get(pk=format_pk)
    return format.populate_format_cards()
