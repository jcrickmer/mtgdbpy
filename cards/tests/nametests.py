# -*- coding: utf-8 -*-

from django.test import TestCase, TransactionTestCase, RequestFactory
from django_nose import FastFixtureTestCase
from cards.models import Color, Rarity, Type, Subtype, PhysicalCard, Card, BaseCard, CardRating, ExpansionSet, FormatBasecard, SearchPredicate, CardManager, SortDirective
FormatNotSpecifiedException = CardManager.FormatNotSpecifiedException
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction
import json
import sys
from cards.views import autocomplete
err = sys.stderr

SKIP_TESTS_REQUIRING_SOLR = True


# class CardManagerROTestCase(FastFixtureTestCase):
class CardManagerROTestCase(TestCase):
    fixtures = ['mtgdbapp_testdata', ]

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_one(self):
        bc = BaseCard.objects.filter(name='Island').first()
        self.assertEquals(bc.name, 'Island')
        self.assertEquals(bc.physicalcard.get_card_name(), 'Island')

    def test_two(self):
        bc = BaseCard.objects.filter(name='Kor Firewalker').first()
        self.assertEquals(bc.name, 'Kor Firewalker')
        self.assertEquals(bc.physicalcard.get_card_name(), bc.name)

    def test_three(self):
        bc = BaseCard.objects.filter(name='Elspeth, Knight-Errant').first()
        self.assertEquals(bc.name, 'Elspeth, Knight-Errant')
        self.assertEquals(bc.physicalcard.get_card_name(), bc.name)

    def test_four(self):
        bc = BaseCard.objects.filter(name='Delver of Secrets').first()
        self.assertEquals(bc.name, 'Delver of Secrets')
        self.assertEquals(bc.physicalcard.get_card_name(), 'Delver of Secrets/Insectile Aberration')

    def test_five(self):
        bc = BaseCard.objects.filter(name='Ravager of the Fells').first()
        self.assertEquals(bc.name, 'Ravager of the Fells')
        self.assertEquals(bc.physicalcard.get_card_name(), 'Huntmaster of the Fells/Ravager of the Fells')

    def test_six(self):
        bc = BaseCard.objects.filter(name='Wear').first()
        self.assertEquals(bc.name, 'Wear')
        self.assertEquals(bc.physicalcard.get_card_name(), 'Wear/Tear')

    def test_seven(self):
        bc = BaseCard.objects.filter(name='Tear').first()
        self.assertEquals(bc.name, 'Tear')
        self.assertEquals(bc.physicalcard.get_card_name(), 'Wear/Tear')

    def test_one_ajax(self):
        if SKIP_TESTS_REQUIRING_SOLR:
            return
        request = self.factory.get('/cards/_nameauto?q=Island')
        response = autocomplete(request)
        data = json.loads(response.content)
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]['name'], 'Island')

    def test_two_ajax(self):
        if SKIP_TESTS_REQUIRING_SOLR:
            return
        request = self.factory.get('/cards/_nameauto?q=Firewalker')
        response = autocomplete(request)
        data = json.loads(response.content)
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]['name'], 'Kor Firewalker')

    def test_three_ajax(self):
        if SKIP_TESTS_REQUIRING_SOLR:
            return
        request = self.factory.get('/cards/_nameauto?q=elspeth+knight')
        response = autocomplete(request)
        data = json.loads(response.content)
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]['name'], 'Elspeth, Knight-Errant')

    def test_four_ajax(self):
        if SKIP_TESTS_REQUIRING_SOLR:
            return
        request = self.factory.get('/cards/_nameauto?q=delver')
        response = autocomplete(request)
        data = json.loads(response.content)
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]['name'], 'Delver of Secrets/Insectile Aberration')

    def test_five_ajax(self):
        if SKIP_TESTS_REQUIRING_SOLR:
            return
        request = self.factory.get('/cards/_nameauto?q=ravager+fells')
        response = autocomplete(request)
        data = json.loads(response.content)
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]['name'], 'Huntmaster of the Fells/Ravager of the Fells')

    def test_six_ajax(self):
        if SKIP_TESTS_REQUIRING_SOLR:
            return
        request = self.factory.get('/cards/_nameauto?q=wear')
        response = autocomplete(request)
        data = json.loads(response.content)
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]['name'], 'Wear/Tear')

    def test_six_ajax(self):
        if SKIP_TESTS_REQUIRING_SOLR:
            return
        request = self.factory.get('/cards/_nameauto?q=wear')
        response = autocomplete(request)
        data = json.loads(response.content)
        # Rest for the Weary' is in this list.
        self.assertEquals(len(data), 2)
        self.assertEquals(data[0]['name'], 'Wear/Tear')

    def test_seven_ajax(self):
        if SKIP_TESTS_REQUIRING_SOLR:
            return
        request = self.factory.get('/cards/_nameauto?q=tear')
        response = autocomplete(request)
        #err.write("RES: {}".format(response.content))
        data = json.loads(response.content)
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]['name'], 'Wear/Tear')
