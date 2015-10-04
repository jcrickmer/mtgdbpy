# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from cards.models import BaseCard
from cards.models import PhysicalCard

#from optparse import make_option

from datetime import datetime, timedelta

from cards.view_utils import convertSymbolsToHTML, make_links_to_cards

import codecs
import operator

import sys
from kitchen.text.converters import getwriter
UTF8Writer = getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)
UTF8Reader = codecs.getreader('utf8')
sys.stdin = UTF8Reader(sys.stdin)


class Command(BaseCommand):

# DO THIS: export PYTHONIOENCODING=utf-8

    def handle(self, *args, **options):
        for line in sys.stdin:
            bc = BaseCard.objects.filter(name=line.strip()).first()
            if bc:
                sys.stdout.write('{}\n'.format(bc.physicalcard_id))
