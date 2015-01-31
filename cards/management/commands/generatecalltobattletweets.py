from django.core.management.base import BaseCommand, CommandError
from cards.models import Card, CardManager, SearchPredicate, SortDirective
from cards.models import CardRating
from cards.models import Format
from cards.models import FormatBasecard
from cards.models import PhysicalCard
from cards.models import BaseCard

import random
import logging

from datetime import datetime, timedelta
from django.utils import timezone

import bitly_api

import sys
out = sys.stdout

format_hashtags = {'Standard': '#mtgstandard',
                   'Modern': '#mtgmodern',
                   'Commander': '#mtgcommander #edh',
                   'TinyLeaders': '#mtgtiny'
                   }


BITLY_API_USER = 'o_l7vkb4uv0'
BITLY_API_KEY = 'R_3cbf22413b0d49b487b71db6b3b4e722'


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Generate some generic tweets to get people battling.'

    def handle(self, *args, **options):
        cur_formats = Format.objects.filter(start_date__lte=datetime.today(), end_date__gte=datetime.today()).order_by('format')

        # connect to bitly
        conn_bitly = bitly_api.Connection(access_token='9708cb7d50550b6409cd93b796990bebdde3edb0')

        for counter in range(0, 1):
            format_count = len(list(cur_formats))
            format_index = int(random.random() * format_count)
            cur_format = cur_formats[format_index]

            spreds = []
            spred = SearchPredicate()
            spred.term = 'format'
            spred.value = cur_format.id
            spreds.append(spred)
            sd = SortDirective()
            sd.term = 'cardrating'
            sd.direction = sd.DESC
            sd.crs_format_id = cur_format.id
            spreds.append(sd)
            card_list = Card.playables.search(spreds)

            rand_index = 5 + int(random.random() * 90)
            comp_index = int(random.random() * 10) - 5 + rand_index
            if comp_index == rand_index:
                comp_index = comp_index + 1

            first_card = card_list[rand_index]
            comp_card = card_list[comp_index]

            tweet = first_card.basecard.name + ' is rated '
            if comp_index > rand_index:
                tweet = tweet + 'better '
            else:
                tweet = tweet + 'worse '
            tweet = tweet + comp_card.basecard.name
            tweet = tweet + ' in ' + format_hashtags[cur_format.formatname] + ' '
            url_raw = 'http://card.ninja/cards/battle/' + cur_format.formatname + '/?bcid=' + str(first_card.basecard.id)
            url_raw = url_raw + '&utm_source=Social&utm_medium=post&utm_campaign=calltobattle'
            bitly = conn_bitly.shorten(url_raw)
            url = out.write(tweet + " " + str(bitly['url']) + "\n[[" + str(url_raw) + "]]\n\n")
