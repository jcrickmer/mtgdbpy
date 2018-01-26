# -*- coding: utf-8 -*-

import datetime
from haystack import indexes
from cards.models import PhysicalCard


class CardIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='get_searchable_document')
    selfreftext = indexes.CharField(model_attr='get_searchable_document_selfref')
    rulestext = indexes.CharField(model_attr='get_searchable_document_rules')
    name = indexes.CharField(model_attr='get_card_name')
    updated_date = indexes.DateTimeField(model_attr='get_last_updated')
    name_auto = indexes.EdgeNgramField(model_attr='get_card_filing_name')

    def get_model(self):
        return PhysicalCard

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(basecard__updated_at__lte=datetime.datetime.now())
