# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from cards.models import Card
from cards.models import Battle
from cards.models import Format
from cards.models import FormatBasecard
from django.utils import timezone

import re

from optparse import make_option

from datetime import datetime, timedelta

import sys
out = sys.stdout


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Generate HTML links to do battles on the cards that are entered on stdin.'

    def add_arguments(self, parser):
        parser.add_argument('--format',
                            dest='format',
                            type='string',
                            default='modern',
                            help='Select the format to battle in. Default is modern.')

    def handle(self, *args, **options):
        regex = re.compile(r'^\d*\s*(?P<cn>\S.+)')
        format_obj = None
        if options['format']:
            format_obj = Format.objects.filter(
                formatname__iexact=options['format'],
                start_date__lte=timezone.now(),
                end_date__gt=timezone.now()).order_by('-end_date').first()

        out.write('<div>Format: ' + format_obj.format + "</div>\n")

        added_cards = []

        for line in sys.stdin:
            cardline = line.rstrip("\n")
            if len(cardline) == 0:
                continue
            mm = regex.match(cardline)
            #out.write("!!! " + str(mm.group('cn')) + "\n")
            cardname = mm.group('cn')
            card = Card.objects.filter(basecard__name__iexact=cardname).first()
            if card is None:
                out.write('Could not find card "' + str(cardname) + '"')
                out.write('<br/>\n')
            elif card in added_cards:
                #out.write('already did this one \n')
                pass
            else:
                added_cards.append(card)
                fbc = FormatBasecard.objects.filter(basecard=card.basecard, format=format_obj).first()
                if fbc is None:
                    out.write('The card "' + card.basecard.name + '" is not in ' + format_obj.formatname)
                    out.write('<br/>\n')
                else:
                    out.write('<a target="battlepane" href="http://card.ninja/cards/battle/')
                    out.write(format_obj.formatname)
                    out.write('/?bcid=')
                    out.write(str(card.basecard.id))
                    out.write('&c=yes">')
                    out.write(card.basecard.name)
                    out.write('</a> ')

                    wincount = Battle.objects.filter(winner_pcard=card.basecard.physicalcard, format=format_obj).count()
                    losecount = Battle.objects.filter(loser_pcard=card.basecard.physicalcard, format=format_obj).count()
                    battlecount = wincount + losecount
                    out.write('[battles: ' + str(battlecount) + ' (' + str(wincount) + '-' + str(losecount) + ')]')
                    out.write('<br/>\n')
