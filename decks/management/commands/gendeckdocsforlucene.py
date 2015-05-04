from django.core.management.base import BaseCommand, CommandError
from cards.models import Card
from cards.models import PhysicalCard
from decks.models import Deck, DeckCard, Tournament, TournamentDeck

import re

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
    )

    def handle(self, *args, **options):

        tdeck_list = TournamentDeck.objects.filter(tournament__format__formatname='Modern')

        for tdeck in tdeck_list:
            deck = tdeck.deck
            dcard_list = DeckCard.objects.filter(deck=deck).order_by('physicalcard')
            text = ''
            for dcard in dcard_list:
                counter = 0
                for counter in range(1, dcard.cardcount):
                    if len(text) > 0:
                        text = text + "\n\n"
                    text = text + dcard.physicalcard.get_searchable_document(include_names=False)

            fileout = codecs.open(options['outdir'] + '/deck_' + str(deck.id), 'w', 'utf-8')
            fileout.write(text + "\n")
            fileout.close()
