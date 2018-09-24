# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from cards.search import searchservice
from cards.models import Card, BaseCard
from cards.models import PhysicalCard
import json

from django.utils import dateparse

import codecs

import sys

from kitchen.text.converters import getwriter

UTF8Writer = getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)
UTF8Reader = codecs.getreader('utf8')
sys.stdin = UTF8Reader(sys.stdin)


class Command(BaseCommand):

    # DO THIS: export PYTHONIOENCODING=utf-8

    def add_arguments(self, parser):
        parser.add_argument('--full', dest='full', action='store_true',
                            help='Rebuild the entire index, not just data that has changed.')

    def handle(self, *args, **options):

        hope = {"Geth's Verdict": ["Diabolic Edict", "Smallpox", "Gnawing Zombie", "Crackling Doom", "To the Slaughter", "Urborg Justice"],
                "Path to Exile": ["Swords to Plowshares", "Cloudshift", "Settle the Wreckage", "Reality Shift", "Blazing Hope",
                                   "Gaze of Justice"]
                }

        for test_name in hope:
            bc = BaseCard.objects.filter(name=test_name).first()
            pc = bc.physicalcard
            sims = pc.find_similar_cards()
            sim_names = [c.basecard.physicalcard.get_card_name() for c in sims]
            match_count = 0
            for res_name in hope[test_name]:
                if res_name in sim_names:
                    match_count += 1
            sys.stdout.write("{}: {:02%}\n".format(pc.get_card_name(),float(match_count) / float(len(hope[test_name]))))
            for res_name in hope[test_name]:
                sys.stdout.write("    {}: {}\n".format(res_name, res_name in sim_names))
