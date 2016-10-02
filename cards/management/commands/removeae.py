# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from cards.models import PhysicalCard
from cards.models import BaseCard
from cards.models import Card
from cards.models import Color, CardColor
from cards.models import Rarity
from cards.models import Type
from cards.models import Subtype
from cards.models import CardType
from cards.models import CardSubtype
from cards.models import Mark
from cards.models import ExpansionSet
from cards.models import Ruling

import logging
import sys
import os
import json


class Command(BaseCommand):

    help = '''Replaces the Ae 'ash' ligature on card names with 'Ae'.'''

    def handle(self, *args, **options):
        bcards = BaseCard.objects.filter(name__contains=u'\u00C6')
        for bcard in bcards:
            bcard.name = bcard.name.replace(u'\u00C6', 'Ae')
            bcard.save()
            sys.stdout.write("updated card {}\n".format(bcard.filing_name))
        bcards = BaseCard.objects.filter(name__contains=u'\u00E6')
        for bcard in bcards:
            bcard.name = bcard.name.replace(u'\u00E6', 'ae')
            bcard.save()
            sys.stdout.write("updated card {}\n".format(bcard.filing_name))
