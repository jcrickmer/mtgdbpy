from django.core.management.base import BaseCommand, CommandError
from cards.models import Card
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
    )

    def handle(self, *args, **options):

        pcard_list = PhysicalCard.objects.all()

        for pcard in pcard_list:
            if pcard.layout in [pcard.TOKEN, pcard.PLANE, pcard.SCHEME, pcard.PHENOMENON, pcard.VANGUARD]:
                continue

            fileout = codecs.open(options['outdir'] + '/' + str(pcard.id), 'w', 'utf-8')
            text = pcard.get_searchable_document(include_names=False)
            fileout.write(text + "\n")
            fileout.close()
