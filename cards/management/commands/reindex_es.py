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

from elasticsearch import Elasticsearch, exceptions

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
        # check the card index
        self.checkCardIndex()

        self.checkCardnameIndex()

        # first, let's get the most recent doc change in ES:
        lmt_q = {
            "query": {"match_all": {}},
            "size": 1,
            "sort": [
                {
                    "_update_datetime": {
                        "order": "desc"
                    }
                }
            ]
        }
        lmt_res = searchservice.search(index='card', body=lmt_q)
        last_time = None
        try:
            sys.stdout.write("timestamp: {}\n".format(json.dumps(lmt_res['hits']['hits'][0]['_source']['_update_datetime'])))
            last_time = dateparse.parse_datetime(lmt_res['hits']['hits'][0]['_source']['_update_datetime'])
        except KeyError:
            # no doc, I guess
            pass
        sys.stdout.write("'card' index last updated {}\n".format(last_time))

        pcs = None

        if not last_time or options['full']:
            sys.stdout.write("Re-indexing entire card database...\n")
            pcs = PhysicalCard.objects.all()
            #pcs = PhysicalCard.objects.filter(pk__gte=15200, pk__lt=15800)
        else:
            cards = Card.objects.filter(updated_at__gte=last_time)
            bc_ids = {}
            for card in cards:
                bc_ids[card.basecard_id] = True
            basecards = BaseCard.objects.filter(updated_at__gte=last_time)
            pc_ids = {}
            for basecard in basecards:
                #sys.stderr.write("bc -> pc {}\n".format(basecard.physicalcard_id))
                pc_ids[basecard.physicalcard_id] = True
            basecards = BaseCard.objects.filter(id__in=[bc_id for bc_id in bc_ids])
            for basecard in basecards:
                pc_ids[basecard.physicalcard_id] = True
            pcs = PhysicalCard.objects.filter(id__in=[pc_id for pc_id in pc_ids])

        total_count = pcs.count()
        counter = 0
        sys.stdout.write("Cards to index: {}\n".format(total_count))
        for pc in pcs:
            searchservice.index_physicalcard(pc)
            counter += 1
            if counter % 100 == 0:
                sys.stdout.write("{:>6} : {:>4.0%} complete\n".format(counter, float(counter) / float(total_count)))
        sys.stdout.write("Complete!\n")

    def checkCardIndex(self):
        index_name = 'card'
        try:
            val = searchservice._es.indices.get_settings(index_name)
        except exceptions.NotFoundError:
            sys.stdout.write("'{}' index does not exist. Creating it...\n".format(index_name))
            searchservice._es.indices.create(index=index_name,
                                             body={})
        return True

    def checkCardnameIndex(self):
        index_name = 'cardname'
        cur_mappings = None
        try:
            cur_mappings = searchservice._es.indices.get_mapping(index_name)
        except exceptions.NotFoundError:
            sys.stdout.write("'{}' index does not exist. Creating it...\n".format(index_name))
            with open('elasticsearch/cardname_settings.json', 'r') as cnsjson_fh:
                cns = json.load(cnsjson_fh)
                sys.stdout.write("Creating '{}' index with:\n{}\n".format(index_name, json.dumps(cns, indent=2)))
                searchservice._es.indices.create(index=index_name,
                                                 body=cns)
        if cur_mappings:
            # we need to validate that there is an ngram field on the "name" property. If there isn't, we should bail.
            # cur_settings['cardname']['settings']['index']
            # BOOKMARK - check to see if there is an ngram mappings on "name"
            try:
                ngram = cur_mappings[index_name]['mappings']['cardname']['properties']['name']['fields']['ngram']
                slug = cur_mappings[index_name]['mappings']['cardname']['properties']['slug']
                lmvid = cur_mappings[index_name]['mappings']['cardname']['properties']['latest_multiverseid']
            except KeyError as ke:
                sys.stdout.write("{} index does not have an 'ngram' field on 'name'.\n".format(index_name))
                sys.stdout.write("{} index Mappings:\n{}\n".format(index_name, json.dumps(cur_mappings, indent=2)))
                sys.stdout.write("Aborting.\n")
                # You may need to drop the old index and start over.
                sys.stdout.write("Try this to get the index started...\n")
                sys.stdout.write("curl -X DELETE '{}:{}/{}?pretty'\n".format(searchservice._host, searchservice._port, index_name))
                sys.stdout.write(
                    "curl -X PUT '{}:{}/{}?pretty' -H 'Content-Type: application/json' -d @elasticsearch/cardname_settings.json\n".format(
                        searchservice._host,
                        searchservice._port,
                        index_name))
                raise ke
        return True
