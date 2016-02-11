# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from cards.models import Card, FormatBasecard, BaseCard
from cards.models import PhysicalCard

import re

from optparse import make_option

from datetime import datetime, timedelta

import codecs

import sys
out = sys.stdout


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Generate HTML links to do battles on the cards that are entered on stdin.'

    option_list = BaseCommand.option_list + (
        make_option('--outdir',
                    dest='outdir',
                    type='string',
                    default='./',
                    help='The directory to stick all of these documents.'),
        make_option('--include-names',
                    dest='include_names',
                    action='store_true',
                    default=False,
                    help='If set, include the name of the card in the output.'),
        make_option('--format-name',
                    dest='formatname',
                    type='string',
                    default='all',
                    help='Only include cards of this particular format. Default is all.'),
    )

    def handle(self, *args, **options):
        pcard_list = list()

        if options['formatname'] == 'all':
            pcard_list = PhysicalCard.objects.filter(basecard__id__gt=0)
        else:
            fbc_list = FormatBasecard.objects.filter(
                format__formatname=options['formatname'],
                # REVISIT - need to come back and set this so that it only grabs the most recent version of the format.
                basecard__cardposition__in=[
                    BaseCard.FRONT,
                    BaseCard.LEFT,
                    BaseCard.UP]).order_by('basecard__physicalcard__id')
            for fbcard in fbc_list:
                pcard = fbcard.basecard.physicalcard
                pcard_list.append(pcard)

        for pcard in pcard_list:
            if pcard.layout in [pcard.TOKEN, pcard.PLANE, pcard.SCHEME, pcard.PHENOMENON, pcard.VANGUARD]:
                continue
            text = pcard.get_searchable_document(include_names=options['include_names'])
            if len(text) < 1:
                sys.stderr.write("Did not get anything valuable back from {}, {}\n".format(pcard.id, pcard.get_card_name()))
            else:
                fileout = codecs.open(options['outdir'] + '/physicalcard_' + str(pcard.id), 'w', 'utf-8')
                fileout.write(text + "\n")
                fileout.close()
