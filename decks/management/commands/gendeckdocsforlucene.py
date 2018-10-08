# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from cards.models import Card
from cards.models import PhysicalCard
from decks.models import Deck, DeckCard, Tournament, TournamentDeck
from django.db.models import Max, Min, Count, Sum, Avg

import re
import numpy

from optparse import make_option

from datetime import datetime, timedelta

import codecs

import sys
out = sys.stdout


class Command(BaseCommand):
    help = 'Generate a deck in a dcoument to be fed into Lucene or Mahout.'

    option_list = BaseCommand.option_list + (
        make_option('--outdir',
                    dest='outdir',
                    type='string',
                    default='./',
                    help='The directory to stick all of these documents.'),
        make_option('--format',
                    dest='formatname',
                    type='string',
                    default='Modern',
                    help='The format to use.'),
    )

    def handle(self, *args, **options):
        t_list = Tournament.objects.filter(format__formatname__iexact=options['formatname']).annotate(deck_count=Count('tournamentdeck'))
        for tourny in t_list:
            if tourny.deck_count > 8:
                tdeck_list = TournamentDeck.objects.filter(tournament=tourny)
                sys.stderr.write('tournament ' + str(tourny.id) + "\n")

                for tdeck in tdeck_list:
                    deck = tdeck.deck
                    sys.stderr.write('deck ' + str(deck.id) + "\n")
                    dcard_list = DeckCard.objects.filter(deck=deck).order_by('physicalcard')
                    text = ''
                    landcount = 0
                    cardcount = 0
                    cmcs = list()
                    for dcard in dcard_list:
                        counter = 0
                        for counter in range(0, dcard.cardcount):
                            bc = dcard.physicalcard.get_face_basecard()
                            if len(text) > 0:
                                text = text + "\n\n"
                            text = text + dcard.physicalcard.get_searchable_document(include_names=True)
                            cardcount = cardcount + 1
                            if bc.is_land():
                                # not sure that this is necessary. term frequency analysis will find all
                                # of the "typeLand" terms and count those.
                                landcount = landcount + 1
                            else:
                                cmcs.append(bc.cmc)
                    if cardcount > 0:
                        fileout = codecs.open(options['outdir'] + '/deck_' + str(deck.id), 'w', 'utf-8')
                        fileout.write('cardcount:{}\n'.format(str(cardcount)))
                        fileout.write('cmcmin:{}\n'.format(str(min(cmcs))))
                        # fileout.write('cmcavg:{}\n'.format(str(sum(cmcs)/float(len(cmcs)))))
                        fileout.write('cmcmean:{}\n'.format(str(numpy.mean(numpy.array(cmcs)))))
                        fileout.write('cmcmax:{}\n'.format(str(max(cmcs))))
                        fileout.write('cmcmedian:{}\n'.format(str(numpy.median(numpy.array(cmcs)))))
                        fileout.write('cmcstddev:{}\n'.format(str(numpy.std(numpy.array(cmcs)))))
                        fileout.write(text + "\n")
                        fileout.close()
