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
UTF8Writer = getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)
UTF8Reader = codecs.getreader('utf8')
sys.stdin = UTF8Reader(sys.stdin)


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Generate HTML links to the cards that are entered on stdin.'

# DO THIS: export PYTHONIOENCODING=utf-8

    def handle(self, *args, **options):
        # assume each line is a card
        all_lines = u''
        for line in sys.stdin:
            line = line.strip()
            all_lines = all_lines + '<li> ' + line + ' </li>\n'

        card_vals = Card.playables.get_simple_cards_list()
        result = '''<h3 class="deck-name">DECK NAME</h3>
<h4 class="deck-byline">by DECK OWNER</h4>
<div style="clear:both; float:left; width: 100%">
  <div style="width:198px; float:left">
    <h4 class="cardlist-category">cards...</h4>
    <ol class="cardlist">
'''
        result = result + make_links_to_cards(all_lines, card_vals, magic_format='onmouseover="cn.updateCard(\'cardarea\', \'{}\');"')
        result = result + '''
    </ol>
  </div>
  <div style="width:198px; float:left">
  </div>
  <div style="width:198px; float:left" id="cardarea">
  </div>
</div>
<script>$(document).ready(function () { cn.updateCard('cardarea', 235597); });</script>
<br style="clear:all"/>
'''
        sys.stdout.write(result)
