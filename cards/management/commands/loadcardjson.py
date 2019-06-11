# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

import logging
import sys
import os

from cards.utils.cardjson import Processor
from cards.utils.cardjson import logger as plogger

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = '''Load up some JSON and add it to the database, if needed.'''

    def add_arguments(self, parser):
        parser.add_argument('input')

    def handle(self, *args, **options):
        #
        # the first (and only) arg should be a filename

        filename = options['input']
        if not os.access(filename, os.R_OK):
            sys.stderr.write("Cannot read file '{}'.\n".format(filename))
            return

        processor = Processor(filename)
        # plogger.addHandler(logging.StreamHandler())
        processor.process()
