# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from cards.models import Card, Format, FormatBasecard, BaseCard, FormatExpansionSet, ExpansionSet, FormatBannedCard
from cards.models import PhysicalCard
from django.db.models import Q
import itertools

from optparse import make_option

from datetime import datetime, timedelta

import errno
import os

import codecs

import sys
out = sys.stdout


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Populate the FormatBasecard table with all of the cards for a format.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--formatid',
            dest='format_id',
            type=int,
            default=0,
            help='The id of the format to populate.'
        )

    def handle(self, *args, **options):
        out.write('format ' + str(options['format_id']) + "\n")
        format_obj = Format.objects.get(pk=options['format_id'])
        out.write('Format: ' + format_obj.format + " (" + format_obj.formatname + ")\n")
        current_count = FormatBasecard.objects.filter(format=format_obj).count()
        out.write('Clearing out ' + str(current_count) + " existing card relationships...\n")
        FormatBasecard.objects.filter(format=format_obj).delete()
        out.write("   completed!\n")

        out.write("Expansion Sets:\n")
        expsets = FormatExpansionSet.objects.filter(format=format_obj)
        if len(expsets) == 0:
            out.write('   none!')
        for expset in expsets:
            out.write('    ' + expset.expansionset.name + "\n")

        out.write("Banned Cards:\n")
        banlist = FormatBannedCard.objects.filter(format=format_obj)
        for bannedcard in banlist:
            out.write('    ' + bannedcard.physicalcard.get_card_name() + "\n")

        out.write("\nWorking...\n")
        format_obj.populate_format_cards()
        out.write("completed!\n")
