# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from cards.models import PhysicalCard, Format
from cards.models import BaseCard
from cards.models import Card
from cards.models import ExpansionSet
from cards.models import CardPrice
from django.db.models import Q
from datetime import datetime, date, timedelta
from django.utils import timezone
import logging
import sys
import time
import traceback
import os
import json
import urllib
from cards.deckbox import generate_auth_key


class Command(BaseCommand):

    help = '''Grab some card prices and update the database.'''

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            dest='count',
            type=int,
            default=10,
            help='The number of card prices to grab.'
        )
        parser.add_argument(
            '--delayseed',
            dest='delayseed',
            type=int,
            default=11,
            help='The seed for a randomish amount of time in seconds to wait between requests to the pricing service.'
        )

    def grab_price(self, mvid):
        auth_key = generate_auth_key(mvid, 'bogus_session_id')
        url = 'https://www.patsgames.com/store/getCardInfo.pl?mvid={}&key={}'.format(mvid, auth_key)
        serialized_data = urllib.request.urlopen(url).read()

        data = json.loads(serialized_data)
        sys.stdout.write("Data: {}\n".format(json.dumps(data)))
        if 'status' in data and data['status'].lower() == 'ok':
            if 'prices' in data:
                for pobj in data['prices']:
                    #sys.stdout.write("MultiverseId {} normal: {} {}\n".format(pobj['mvid'], pobj['normalprice'], pobj['normalsale']))
                    card = Card.objects.filter(multiverseid=pobj['mvid']).first()
                    if card.basecard.name in ('Plains', 'Island', 'Swamp', 'Mountain', 'Forest') and int(pobj['normalprice']) > 99999:
                        # Pat doesn't keep basic land prices. So make it up. Note that this could
                        # be very wrong for things like Unhinged and LEA.
                        ncp = CardPrice(card=card, printing='normal')
                        ncp.price = 0.10
                        ncp.price_discounted = False
                        ncp.save()
                        sys.stdout.write(u"{}\n".format(ncp))
                    elif int(pobj['normalprice']) < 99999:
                        ncp = CardPrice(card=card, printing='normal')
                        ncp.price = pobj['normalprice']
                        ncp.price_discounted = pobj['normalsale'] == 1
                        ncp.save()
                        sys.stdout.write(u"{}\n".format(ncp))

                    if 'foilprice' in pobj and int(pobj['foilprice']) < 99999:
                        fcp = CardPrice(card=card, printing='foil')
                        fcp.price = pobj['foilprice']
                        fcp.price_discounted = pobj['foilsale'] == 1
                        fcp.save()
                        sys.stdout.write(u"{}\n".format(fcp))

    def handle(self, *args, **options):
        #logger = logging.getLogger(__name__)
        # the first (and only) arg should be a filename

        mvids = self.mvids_of_interest("modern")
        mvids_s = self.mvids_of_interest("standard")
        mvids_l = self.mvids_of_interest("legacy")
        mvids_c = self.mvids_of_interest("commander")
        mvids = mvids + mvids_s + mvids_l + mvids_c

        dedup = list()
        for val in mvids:
            if val not in dedup:
                dedup.append(val)
        mvids = dedup

        yesterday = timezone.now() - timedelta(days=1)
        cardprices = CardPrice.objects.filter(card__multiverseid__in=mvids, at_datetime__gte=yesterday)
        cardprice_mvids = [cp.card.multiverseid for cp in cardprices]
        grab_actions = 0
        for mvid in mvids:
            if mvid not in cardprice_mvids:
                if grab_actions < options['count']:
                    sys.stdout.write("+need to grab price id {}\n".format(mvid))
                    self.grab_price(mvid)
                    grab_actions = grab_actions + 1
                    time.sleep(options['delayseed'])
                else:
                    sys.stdout.write("-missing id {} but not going for it\n".format(mvid))
            else:
                sys.stdout.write("=have id {}\n".format(mvid))

    def mvids_of_interest(self, formatname="modern"):
        top_formats = Format.objects.filter(formatname__iexact=formatname, start_date__lte=timezone.now()).order_by('-start_date')
        top_format = None
        next_format = None
        result = {}
        try:
            top_format = top_formats[0]
            next_format = top_formats[1]
        except IndexError:
            return result.keys()

        up_raw_sql = '''
SELECT s1.physicalcard_id AS id,
       100 * s2.percentage_of_all_cards AS prev_percentage,
       100 * s1.percentage_of_all_cards AS current_percentage,
       100 * (s1.percentage_of_all_cards - s2.percentage_of_all_cards) AS delta,
       case when s2.percentage_of_all_cards = 0 then NULL else 100 * (s1.percentage_of_all_cards - s2.percentage_of_all_cards) / s2.percentage_of_all_cards end AS per_change,
       100 * (s1.deck_count / fs1.tournamentdeck_count) decks_current_percentage,
       100 * (s2.deck_count / fs2.tournamentdeck_count) decks_prev_percentage,
       case when fs2.tournamentdeck_count = 0 then NULL else 100 * ((s1.deck_count / fs1.tournamentdeck_count) - (s2.deck_count / fs2.tournamentdeck_count)) / (s2.deck_count / fs2.tournamentdeck_count) end AS decks_per_change
  FROM formatcardstat s1
       JOIN basecard bc ON s1.physicalcard_id = bc.physicalcard_id AND bc.cardposition IN ('F','L','U')
       JOIN formatstat fs1 ON fs1.format_id = s1.format_id AND s1.format_id = %s
       LEFT JOIN formatcardstat s2 ON s1.physicalcard_id = s2.physicalcard_id AND s2.format_id = %s
       LEFT JOIN formatstat fs2 ON fs2.format_id = s2.format_id
 WHERE s1.percentage_of_all_cards > s2.percentage_of_all_cards
 ORDER BY delta DESC LIMIT 50'''

        foo = PhysicalCard.objects.raw(up_raw_sql, [top_format.id, next_format.id])
        for pc in foo:
            if pc.get_card_name() in ('Plains', 'Island', 'Swamp', 'Mountain', 'Forest'):
                pass
            else:
                result[self.likely_printing_mvid(pc)] = True

        down_raw_sql = '''
SELECT s1.physicalcard_id AS id,
       100 * s2.percentage_of_all_cards AS prev_percentage,
       100 * s1.percentage_of_all_cards AS current_percentage,
       100 * (s2.percentage_of_all_cards - s1.percentage_of_all_cards) AS delta,
       case when s2.percentage_of_all_cards = 0 then NULL else 100 * (((s2.percentage_of_all_cards - s1.percentage_of_all_cards) / s2.percentage_of_all_cards) - 1) end AS per_change,
       100 * (s1.deck_count / fs1.tournamentdeck_count) decks_current_percentage,
       100 * (s2.deck_count / fs2.tournamentdeck_count) decks_prev_percentage,
       case when fs2.tournamentdeck_count = 0 then NULL else 100 * ((s1.deck_count / fs1.tournamentdeck_count) - (s2.deck_count / fs2.tournamentdeck_count)) / (s2.deck_count / fs2.tournamentdeck_count) end AS decks_per_change
  FROM formatcardstat s1
       JOIN basecard bc ON s1.physicalcard_id = bc.physicalcard_id AND bc.cardposition IN ('F','L','U')
       JOIN formatstat fs1 ON fs1.format_id = s1.format_id AND s1.format_id = %s
       LEFT JOIN formatcardstat s2 ON s1.physicalcard_id = s2.physicalcard_id AND s2.format_id = %s
       LEFT JOIN formatstat fs2 ON fs2.format_id = s2.format_id
 WHERE s1.percentage_of_all_cards < s2.percentage_of_all_cards
 ORDER BY delta DESC LIMIT 50'''
        tdown = PhysicalCard.objects.raw(down_raw_sql, [top_format.id, next_format.id])
        for pc in tdown:
            if pc.get_card_name() in ('Plains', 'Island', 'Swamp', 'Mountain', 'Forest'):
                pass
            else:
                result[self.likely_printing_mvid(pc)] = True

        top_raw_sql = '''
SELECT s1.physicalcard_id AS id,
       100 * s2.percentage_of_all_cards AS prev_percentage,
       100 * s1.percentage_of_all_cards AS current_percentage,
       100 * (s2.percentage_of_all_cards - s1.percentage_of_all_cards) AS delta,
       case when s2.percentage_of_all_cards = 0 then NULL else 100 * (((s2.percentage_of_all_cards - s1.percentage_of_all_cards) / s2.percentage_of_all_cards) - 1) end AS per_change,
       100 * (s1.deck_count / fs1.tournamentdeck_count) decks_current_percentage,
       100 * (s2.deck_count / fs2.tournamentdeck_count) decks_prev_percentage,
       case when fs2.tournamentdeck_count = 0 then NULL else 100 * ((s1.deck_count / fs1.tournamentdeck_count) - (s2.deck_count / fs2.tournamentdeck_count)) / (s2.deck_count / fs2.tournamentdeck_count) end AS decks_per_change
  FROM formatcardstat s1
       JOIN basecard bc ON s1.physicalcard_id = bc.physicalcard_id AND s1.format_id = %s AND bc.cardposition IN ('F','L','U')
       JOIN formatstat fs1 ON fs1.format_id = s1.format_id
       LEFT JOIN formatcardstat s2 ON s1.physicalcard_id = s2.physicalcard_id AND s2.format_id = %s
       LEFT JOIN formatstat fs2 ON fs2.format_id = s2.format_id
 ORDER BY s1.percentage_of_all_cards DESC LIMIT 100'''
        top = PhysicalCard.objects.raw(top_raw_sql, [top_format.id, next_format.id])
        for pc in top:
            if pc.get_card_name() in ('Plains', 'Island', 'Swamp', 'Mountain', 'Forest'):
                pass
            else:
                result[self.likely_printing_mvid(pc)] = True

        realresult = list()
        for rk in result.keys():
            realresult.append(rk)
        return realresult

    expsets = ExpansionSet.objects.exclude(
        name__icontains='clash pack').exclude(
        name__icontains='duel deck').exclude(
            name__icontains='from the vault').exclude(
                name__icontains='box set').exclude(
                    name__icontains='promo').exclude(
                        name__icontains='gift box').exclude(
                            name__icontains='starter').exclude(
                                name__icontains='premium').exclude(
                                    abbr__regex=r'^p[A-Za-z]{3}$').exclude(abbr='LEA')

    def likely_printing_mvid(self, pcard):
        """ pcard is a PhysicalCard. """
        card = Card.objects.filter(basecard__physicalcard=pcard, expansionset__in=self.expsets).order_by('multiverseid').first()
        if card.multiverseid == 1084:
            # Urza's Power Plant
            return 4193
        elif card.multiverseid == 1080:
            # Urza's Mine
            return 4192
        elif card.multiverseid == 1088:
            return 4194
        elif card.multiverseid == 1849:
            return 413634
        elif card.multiverseid == 270733:
            return 413748
        elif card.multiverseid == 5556:
            return 21153
        elif card.multiverseid == 265156:
            return 376260
        elif card.multiverseid == 2949:
            return 11399
        else:
            return card.multiverseid
