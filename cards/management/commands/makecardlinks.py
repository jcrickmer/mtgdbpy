# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from cards.models import Card
from cards.models import PhysicalCard

#from optparse import make_option

from datetime import datetime, timedelta

from cards.view_utils import convertSymbolsToHTML, make_links_to_cards

import codecs
import operator

import sys
from kitchen.text.converters import getwriter


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Generate HTML links to the cards that are entered on stdin.'

    def handle(self, *args, **options):
        all_lines = u''
        for line in sys.stdin:
            all_lines = all_lines + line

        card_vals = Card.playables.get_simple_cards_list()

        result = make_links_to_cards(all_lines, card_vals)

        sys.stdout.write(result)
