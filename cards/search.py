# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

from django.conf import settings

from elasticsearch import Elasticsearch, exceptions
import sys
from .models import PhysicalCard


class SearchService(object):

    def __init__(self, *args, **kwargs):
        self._host = "localhost"
        self._port = 9200
        try:
            self._host = settings.ELASTICSEARCH_HOST
        except BaseException:
            logger.info(
                'Search Service connecting to default host "{}" because ELASTICSEARCH_HOST is not set.'.format(
                    self._host))
        try:
            self._port = settings.ELASTICSEARCH_PORT
        except BaseException:
            logger.info(
                'Search Service connecting to default post "{}" because ELASTICSEARCH_PORT is not set.'.format(
                    self._port))
        self._es = Elasticsearch(hosts=[{"host": self._host, "port": self._port}, ])

        self._index_name = 'card'
        try:
            self._index_name = settings.ELASTICSEARCH_CARD_INDEX
        except BaseException:
            logger.info(
                'Search Service connecting to default index "{}" because ELASTICSEARCH_CARD_INDEX is not set.'.format(
                    self._index_name))

        # index=getattr(settings, ELASTICSEARCH_CARD_INDEX, 'card'),
        # this enables us to test within the same elastic search instance as is configured (and hopefully running),
        # but not pollute the data that is already in there when we run tests.

        #super().__init__(*args, **kwargs)

    def index_physicalcard(self, physicalcard):
        """

        :type physicalcard: cards.models.PhysicalCard
        """
        result = None
        if physicalcard is not None and not physicalcard.isOrphan():
            doc = physicalcard.get_es_searchable_document()
            # note that the ELASTICSEARCH_CARD_INDEX will not be properly overriden in testing, I think because
            # matchingservice is instantiated before those overrides can happen. So, we are getting from settings when we
            # need it.
            #sys.stderr.write("matchingservice is indexing card {}\n".format(doc))
            logger.debug("Indexing PhysicalCard {} with doc {}\n".format(physicalcard.pk, doc))
            try:
                result = self._es.index(index=self._index_name,
                                        doc_type='physicalcard',
                                        id=int(physicalcard.pk),
                                        body=doc)
            except BaseException as be:
                raise be
            logger.debug("Indexed PhysicalCard {} with result {}\n".format(physicalcard.pk, result))

            try:
                # adding both the card name and the card filing name, so that we can work around punctuation
                cn_s = physicalcard.get_card_name().lower().split()
                cn_s += physicalcard.get_card_filing_name().lower().split()
                suggest_input = []
                for cnp in cn_s:
                    if cnp != '/' and cnp not in suggest_input:
                        suggest_input.append(cnp)

                card = physicalcard.get_latest_card()
                result = self._es.index(index='cardname',
                                        doc_type='cardname',
                                        id=int(physicalcard.pk),
                                        body={'name': physicalcard.get_card_name(),
                                              'slug': card.url_slug(),
                                              'name_parts': " ".join(suggest_input),
                                              'latest_multiverseid': card.multiverseid,
                                              })
            except BaseException as be:
                sys.stderr.write("Error working on PhysicalCard.id {}\n".format(physicalcard.pk))
                sys.stderr.write("{}\n".format(be))
                sys.stderr.write("continuing...\n")

        return result

    # def match_cards(self, opportunity):
    #    qdoc = opportunity.build_query_doc()
    #    logger.debug("Searching for Cards with query {}\n".format(qdoc))
    #    return self.search(index=self._index_name, body=qdoc)

    def search(self, *args, **kwargs):
        # pass on through...
        try:
            result = self._es.search(*args, **kwargs)
            #system_condition.matchingservice_status = system_condition.ONLINE
            return result
        except BaseException as be:
            #system_condition.matchingservice_status = system_condition.OFFLINE
            #system_condition.matchingservice_last_exception = be
            raise be

    def force_refresh(self):
        """Force the underlying index to refresh, which should merge all pending changes in for searching."""
        try:
            self._es.transport.perform_request('POST', '/{}/_refresh'.format(self._index_name))
            #system_condition.matchingservice_status = system_condition.ONLINE
        except BaseException as be:
            #system_condition.matchingservice_status = system_condition.OFFLINE
            #system_condition.matchingservice_last_exception = be
            raise be


searchservice = SearchService()

# Make sure that the service is running when we get started.
tryagain = False
errmsg = 'Unable to connect to ElasticSearch instance and/or index.' + \
    ' Host: "{}"; Port: "{}"; Index: "{}"'.format(searchservice._host, searchservice._port, searchservice._index_name)
try:
    searchservice.search(index=searchservice._index_name, body={"query": {"query_string": {"query": "connected"}}})
except exceptions.NotFoundError:
    # index does not yet exist. Make it. With a random card.
    pc = PhysicalCard.objects.all().first()
    searchservice.index_physicalcard(pc)
    tryagain = True
# except exceptions.ConnectionError as ce:
except BaseException:
    logger.fatal(msg=errmsg, exc_info=True)
if tryagain:
    try:
        searchservice.search(index=searchservice._index_name, body={"query": {"query_string": {"query": "connected"}}})
    except BaseException:
        logger.fatal(msg=errmsg, exc_info=True)
        # sys.exit()
