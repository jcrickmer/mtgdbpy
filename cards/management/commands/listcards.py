# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from cards.models import PhysicalCard, Format
from cards.models import BaseCard
from cards.models import Card
from cards.models import ExpansionSet
from cards.models import CardPrice
from django.db.models import Q
from datetime import datetime, date, timedelta
import sys


class Command(BaseCommand):

    help = '''List out all cards in the database by Multiversid, one card per line.'''

    def handle(self, *args, **options):
        cards = Card.objects.all().order_by('multiverseid')
        #cards = Card.objects.filter(multiverseid__gt=450000).order_by('multiverseid')
        for card in cards:
            sys.stdout.write('{}|'.format(card.multiverseid))
            sys.stdout.write('{}|'.format(card.basecard.name))
            sys.stdout.write('{}|'.format(card.basecard.filing_name))
            sys.stdout.write('{}|'.format(card.basecard.physicalcard.get_card_name()))
            sys.stdout.write('{}|'.format(card.expansionset.abbr))
            sys.stdout.write('{}|'.format(card.expansionset.name))

            try:
                sys.stdout.write('{}'.format(card.rarity.rarity))
            except BaseException:
                pass
            sys.stdout.write('|')

            sys.stdout.write('{}|'.format(card.card_number))
            if card.mark:
                sys.stdout.write('{}|'.format(card.mark.mark))
            else:
                sys.stdout.write('{}|'.format(''))
            sys.stdout.write('{}|'.format(card.basecard.physicalcard.id))
            sys.stdout.write('{}|'.format(card.basecard.id))
            sys.stdout.write('{}|'.format(card.basecard.cardposition))
            sys.stdout.write('{}|'.format(card.basecard.mana_cost))
            sys.stdout.write('{}|'.format(card.basecard.cmc))
            sys.stdout.write('{}|'.format(card.basecard.power))
            sys.stdout.write('{}|'.format(card.basecard.toughness))
            sys.stdout.write('{}|'.format(card.basecard.loyalty))
            clean_rt = str(card.basecard.rules_text)
            clean_rt = clean_rt.replace("\n", " ")
            clean_rt = clean_rt.replace("|", "_")
            sys.stdout.write('{}|'.format(clean_rt))
            sys.stdout.write('{}|'.format(card.basecard.ispermanent))
            sys.stdout.write('{}|'.format(card.basecard.get_full_type_str()))
            clean_colors = str(card.basecard.physicalcard.get_searchable_document_color())
            clean_colors = clean_colors.replace("\n", " ")
            sys.stdout.write('{}|'.format(clean_colors))

            sys.stdout.write("\n")
