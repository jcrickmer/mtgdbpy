from django.core.management.base import BaseCommand, CommandError
from cards.models import Color
from cards.models import Rarity
from cards.models import BattleTest

#from django.core.exceptions import DoesNotExist

import logging
import sys


class Command(BaseCommand):

    help = '''Checks to see if the cards database is blank, and if it is, then it adds the very basics to allow to get the database initialized. Adds colors and rarities.'''

    def handle(self, *args, **options):
        #logger = logging.getLogger(__name__)

        self.init_colors()

        self.init_rarities()

        self.init_battletests()

    def init_colors(self):
        colors = [['W', 'white'],
                  ['U', 'blue'],
                  ['B', 'black'],
                  ['R', 'red'],
                  ['G', 'green'],
                  ['c', 'colorless']]

        for color in colors:
            dbc = None
            try:
                dbc = Color.objects.get(pk=color[0])
            except Color.DoesNotExist:
                dbc = Color()
                dbc.id = color[0]

            dbc.color = color[1]
            dbc.save()

    def init_rarities(self):
        rarities = [['b', 'Basic Land', 0],
                    ['c', 'Common', 1],
                    ['u', 'Uncommon', 2],
                    ['r', 'Rare', 3],
                    ['m', 'Mythic Rare', 4],
                    ['s', 'Special', 5]]
        for rarity in rarities:
            dbr = None

            try:
                dbr = Rarity.objects.get(pk=rarity[0])
            except Rarity.DoesNotExist:
                dbr = Rarity()
                dbr.id = rarity[0]

            dbr.rarity = rarity[1]
            dbr.sortorder = rarity[2]
            dbr.save()

    def init_battletests(self):
        bt = BattleTest(name='subjective')
        bt.save()
