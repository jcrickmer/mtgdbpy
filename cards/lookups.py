# -*- coding: utf-8 -*-

from ajax_select import LookupChannel
from django.utils.html import escape
#from django.db.models import Q
from cards.models import PhysicalCard
from cards.models import ExpansionSet
from cards.models import Card


class PhysicalCardLookup(LookupChannel):

    model = PhysicalCard

    def get_query(self, q, request):
        return PhysicalCard.objects.filter(basecard__name__icontains=q)

    def get_result(self, obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.get_card_name()

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        # return u"%s<div><i>%s</i></div>" % (escape(obj.name),escape(obj.email))
        return obj.get_card_name()


class ExpansionSetLookup(LookupChannel):

    model = ExpansionSet

    def get_query(self, q, request):
        return ExpansionSet.objects.filter(name__icontains=q)

    def get_result(self, obj):
        """ result is the simple text that is the completion of what the person typed """
        return obj.name

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        # return u"%s<div><i>%s</i></div>" % (escape(obj.name),escape(obj.email))
        return obj.name


class CardLookup(LookupChannel):

    model = Card

    def get_query(self, q, request):
        return Card.objects.filter(basecard__name__icontains=q)

    def get_result(self, obj):
        """ result is the simple text that is the completion of what the person typed """
        return '{} [{}]'.format(obj.basecard.name, obj.expansionset.abbr)

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        # return u"%s<div><i>%s</i></div>" % (escape(obj.name),escape(obj.email))
        return self.get_result(obj)
