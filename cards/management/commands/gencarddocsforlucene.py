# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from cards.models import Card, FormatBasecard, BaseCard, Color
from cards.models import PhysicalCard
from django.db.models import Q
import re
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
    help = 'Generate HTML links to do battles on the cards that are entered on stdin.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--outdir',
            dest='outdir',
            # type=string,
            default='./',
            help='The directory to stick all of these documents.'
        )
        parser.add_argument(
            '--include-names',
            dest='include_names',
            action='store_true',
            default=False,
            help='If set, include the name of the card in the output.'
        )
        parser.add_argument(
            '--format-name',
            dest='formatname',
            # type=string,
            default='all',
            help='Only include cards of this particular format. Default is all.'
        )
        parser.add_argument(
            '--clustertest',
            dest='clustertest',
            action='store_true',
            default=False,
            help='Generate ~408 cards used for cluster testing. 25 destroy creatures, 50 lands, 25 gain life, 50 flying creatures, 50 seaching creatures, 25 counter spells, 25 burn spells, 25 artifacts with tap abilities.'
        )
        parser.add_argument(
            '--test_id',
            dest='test_id',
            type=int,
            default=0,
            help='The test number to run, for multiple strategies. Only works in conjunction with --clustertest, otherwise y=you just get what is in PhysicalCard.get_searchable_document().')

    def handle(self, *args, **options):
        pcard_list = list()

        if options['clustertest']:
            d_pcard_list = PhysicalCard.objects.filter(Q(id__lte=15876),
                                                       Q(basecard__rules_text__icontains='destroy'),
                                                       Q(basecard__rules_text__icontains='target'),
                                                       Q(basecard__rules_text__icontains='creature')).order_by('-basecard__card__multiverseid')[:25]
            land_pcard_list = PhysicalCard.objects.filter(
                Q(id__lte=15876), Q(basecard__cardtype__type__type='Land')).order_by('-basecard__card__multiverseid')[:50]
            gl_pcard_list = PhysicalCard.objects.filter(Q(id__lte=15876),
                                                        Q(basecard__rules_text__icontains='gain'),
                                                        Q(basecard__rules_text__icontains='life')).order_by('-basecard__card__multiverseid')[:25]
            flying_pcard_list = PhysicalCard.objects.filter(Q(id__lte=15876), Q(basecard__rules_text__contains='Flying'), Q(
                basecard__cardtype__type__type='Creature')).order_by('-basecard__card__multiverseid')[:50]
            search_pcard_list = PhysicalCard.objects.filter(Q(id__lte=15876), Q(basecard__rules_text__icontains='search'), Q(
                basecard__cardtype__type__type='Creature')).order_by('-basecard__card__multiverseid')[:50]
            counter_pcard_list = PhysicalCard.objects.filter(Q(id__lte=15876),
                                                             Q(basecard__rules_text__icontains='counter'),
                                                             Q(basecard__rules_text__icontains='target'),
                                                             Q(basecard__rules_text__icontains='spell')).order_by('-basecard__card__multiverseid')[:25]
            burn_pcard_list = PhysicalCard.objects.filter(Q(id__lte=15876),
                                                          Q(basecard__rules_text__icontains='deal'),
                                                          Q(basecard__rules_text__icontains='damage'),
                                                          Q(basecard__rules_text__icontains='target'),
                                                          Q(basecard__rules_text__icontains='creature')).order_by('-basecard__card__multiverseid')[:25]
            artifact_pcard_list = PhysicalCard.objects.filter(Q(id__lte=15876), Q(basecard__rules_text__icontains='{t}'), Q(
                basecard__cardtype__type__type='Artifact')).order_by('-basecard__card__multiverseid')[:25]
            pcard_list = itertools.chain(
                d_pcard_list,
                land_pcard_list,
                gl_pcard_list,
                flying_pcard_list,
                search_pcard_list,
                counter_pcard_list,
                burn_pcard_list,
                artifact_pcard_list)
        elif options['formatname'] == 'all':
            pcard_list = PhysicalCard.objects.all()
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

        # IF we are doing the clustertest, let's output a CSV file with relevant details.
        clustertest_csv_out = None
        white = Color.objects.get(pk='W')
        blue = Color.objects.get(pk='U')
        black = Color.objects.get(pk='B')
        red = Color.objects.get(pk='R')
        green = Color.objects.get(pk='G')

        for pcard in pcard_list:
            if pcard.layout in [pcard.TOKEN, pcard.PLANE, pcard.SCHEME, pcard.PHENOMENON, pcard.VANGUARD]:
                continue
            text = ""
            if options['clustertest']:
                if clustertest_csv_out is None:
                    clustertest_csv_out = codecs.open(options['outdir'] + '/clustertest_cards.csv', 'w', 'utf-8')
                    clustertest_csv_out.write('card,cost,cmc,white,blue,black,red,green,type,subtype,text,power,toughness,url\n')
                text = getattr(self, 'strategy{:03d}'.format(options['test_id']))(pcard)
                bcard = pcard.get_face_basecard()
                bccolors = bcard.colors.all()
                rt = bcard.rules_text
                if rt is None:
                    rt = ''
                else:
                    rt = rt.replace('"', "'").replace("\n", " ")
                clustertest_csv_out.write('"{}","{}",{},{},{},{},{},{},{},{},"{}",{},{},"http://card.ninja/cards/{}/"\n'.format(pcard.get_card_name(),
                                                                                                                                bcard.mana_cost,
                                                                                                                                bcard.cmc,
                                                                                                                                white in bccolors,
                                                                                                                                blue in bccolors,
                                                                                                                                black in bccolors,
                                                                                                                                red in bccolors,
                                                                                                                                green in bccolors,
                                                                                                                                ' '.join([t.type for t in bcard.types.all()]),
                                                                                                                                ' '.join([t.subtype for t in bcard.subtypes.all()]),
                                                                                                                                rt,
                                                                                                                                bcard.power,
                                                                                                                                bcard.toughness,
                                                                                                                                pcard.get_latest_url_part()))
            else:
                text = pcard.get_searchable_document(include_names=options['include_names'])
            if len(text) < 1:
                sys.stderr.write("Did not get anything valuable back from {}, ".format(pcard.id))
                try:
                    sys.stderr.write("{}\n".format(pcard.get_card_name()))
                except AttributeError:
                    sys.stderr.write("_could not determine name - possibly no basecard for this physicalcard_\n")
            else:
                mkdir_p(options['outdir'])
                fileout = codecs.open(options['outdir'] + '/physicalcard_' + str(pcard.id), 'w', 'utf-8')
                fileout.write(text + "\n")
                fileout.close()
        if clustertest_csv_out is not None:
            clustertest_csv_out.close()

    def strategy000(self, pcard):
        return pcard.get_searchable_document(include_names=False)

    def strategy001(self, pcard):
        return self.strategy000(pcard)

    def strategy002(self, pcard):
        return self.strategy000(pcard)

    def strategy003(self, pcard):
        return self.strategy000(pcard)

    def strategy004(self, pcard):
        return self.strategy000(pcard)

    def strategy005(self, pcard):
        return self.strategy000(pcard)

    def strategy006(self, pcard):
        return self.strategy000(pcard)

    def strategy007(self, pcard):
        return self.strategy000(pcard)

    def strategy008(self, pcard):
        return self.strategy000(pcard)

    def strategy009(self, pcard):
        return self.strategy000(pcard)

    def strategy010(self, pcard):
        return self.strategy000(pcard)

    def strategy011(self, pcard):
        return self.strategy000(pcard)

    def strategy012(self, pcard):
        return self.strategy000(pcard)

    def strategy013(self, pcard):
        return self.strategy000(pcard)

    def strategy014(self, pcard):
        return self.strategy000(pcard)

    def strategy015(self, pcard):
        return self.strategy000(pcard)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
