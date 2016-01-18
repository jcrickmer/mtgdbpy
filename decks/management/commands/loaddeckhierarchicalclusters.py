from django.core.management.base import BaseCommand, CommandError
from cards.models import Card
from cards.models import PhysicalCard
from decks.models import Deck, DeckCard, Tournament, TournamentDeck, DeckCluster, DeckClusterDeck

import re

from optparse import make_option

from datetime import datetime, timedelta

import codecs

import sys
out = sys.stdout


class Command(BaseCommand):
    help = 'Generate a deck in a document to be fed into Lucene or Mahout.'

    option_list = BaseCommand.option_list + (
        make_option('--input',
                    dest='input',
                    type='string',
                    default='./hierarchical_clusters.csv',
                    help='The csv file that Orange will output. Expected to have deck id as first column, cluster as last column.'),
    )

    def handle(self, *args, **options):

        line_re = re.compile(r'^deck_([0-9]+),.+,C(luster )?([0-9]+)$')
        filein = codecs.open(options['input'], 'r', 'utf-8')
        for line in filein:
            lmatch = line_re.search(line)
            if lmatch:
                key = lmatch.group(3)
                distance = 1.0
                deck_id = lmatch.group(1)
                dc = DeckCluster.objects.filter(formatname='Modern', clusterkey=int(key)).first()
                if dc is None:
                    dc = DeckCluster(formatname='Modern', clusterkey=int(key), name='Cluster {}'.format(str(key)))
                    dc.save()
                    out.write('Created new DeckCluster for Key {}\n'.format(str(key)))
                    dc = DeckCluster.objects.filter(formatname='Modern', clusterkey=int(key)).first()
                deck_obj = Deck.objects.get(pk=int(deck_id))
                dcd = DeckClusterDeck(deckcluster=dc, distance=float(distance), deck=deck_obj)
                dcd.save()
                out.write('Key {}, dist {}, deck id {}\n'.format(str(key), str(distance), str(deck_id)))
        filein.close()
