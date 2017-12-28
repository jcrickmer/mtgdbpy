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

    help = '''Updates the card filing names in the database.'''

    def handle(self, *args, **options):
        bcards = BaseCard.objects.all()
        for bcard in bcards:
            old_filing_name = bcard.filing_name
            updated_filing_name = bcard.make_filing_name(bcard.name)
            if old_filing_name != updated_filing_name:
                bcard.filing_name = updated_filing_name
                bcard.save()
                sys.stdout.write(u"Updated: {} -> {}\n".format(bcard.name, bcard.filing_name))
            else:
                sys.stdout.write(u"Skipped: {} -> {}\n".format(bcard.name, bcard.filing_name))
