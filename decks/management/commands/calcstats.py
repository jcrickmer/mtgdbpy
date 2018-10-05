# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from decks.models import Deck
from decks.models import Tournament
from decks.models import TournamentDeck
from decks.models import FormatStat
from decks.models import FormatCardStat
from cards.models import Card
from cards.models import Format
from cards.models import FormatBasecard
from cards.models import PhysicalCard

from optparse import make_option

from datetime import datetime, timedelta
from django.utils import timezone
from dateutil.parser import parse as dtparse


class Command(BaseCommand):
    help = '''Recalculate all of the card stats.'''

    def add_arguments(self, parser):
        parser.add_argument(
            '-a', '--all',
            dest='all_stats',
            action='store_true',
            default=False,
            help='Calc both formats and cards.')

        parser.add_argument('-f', '--formats',
                            dest='format_stats',
                            action='store_true',
                            default=False,
                            help='Calc stats for formats.')

        parser.add_argument('-c', '--cards',
                            dest='card_stats',
                            action='store_true',
                            default=False,
                            help='Calc stats for cards.')

        parser.add_argument('-n', '--new-only',
                            dest='new_only',
                            action='store_true',
                            help='Only calculate formats or cards that have not been calculated yet.')

        parser.add_argument('-s', '--start-date',
                            dest='start_date',
                            default='2014-09-01',
                            help='Start with formats that are on or after this date.')

        parser.add_argument('-e', '--end-date',
                            dest='end_date',
                            default='2025-12-31',
                            help='End with formats that are on or before this date.')

        parser.add_argument('--formatname',
                            dest='formatname',
                            help='Calculate stats for specific format.')

    def handle(self, *args, **options):
        sdate = None
        edate = None
        try:
            sdate = dtparse(options['start_date'])
        except ValueError as ve:
            self.stderr.write("Could not parse start-date '{}'\n".format(options['start_date']))
            return
        try:
            edate = dtparse(options['end_date'])
        except ValueError as ve:
            self.stderr.write("Could not parse end-date '{}'\n".format(options['end_date']))
            return

        if not options['all_stats'] and not options['format_stats'] and not options['card_stats']:
            self.stderr.write("No action taken. Specify all, formats, or cards.\n")

        fn = None
        if 'formatname' in options:
            fn = options['formatname']

        if options['all_stats'] or options['format_stats']:
            self.stderr.write("formats...\n")
            FormatStat.calc_all(new_only=options['new_only'], start_date=sdate, end_date=edate, only_formatname=fn)

        if options['all_stats'] or options['card_stats']:
            self.stderr.write("cards...\n")
            FormatCardStat.calc_all(new_only=options['new_only'], start_date=sdate, end_date=edate, only_formatname=fn)
