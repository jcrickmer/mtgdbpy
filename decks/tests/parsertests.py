from django.test import TestCase, TransactionTestCase
from django_nose import FastFixtureTestCase

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction

from datetime import datetime

from cards.models import PhysicalCard, Format, Color, BaseCard, Card
from decks.models import Deck, DeckCard

from cards.tests.helper import TestLoadHelper
from django.core.cache import cache

import sys
err = sys.stderr


class DecksTestCase(TestCase):

    exempt_from_fixture_bundling = True

    def test_empty(self):
        cache.clear()
        tlh = TestLoadHelper()
        tlh.basics_loader()

        tformat = Format.objects.all().first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = tformat

        tdeck.save()

        decklist = ''
        tdeck.set_cards_from_text(decklist)

        self.assertEquals(tdeck.get_card_count(), 0)

    def test_deck_mountain(self):
        cache.clear()
        tlh = TestLoadHelper()
        tlh.basics_loader()

        tformat = Format.objects.filter(format='Standard_2015-01-23').first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = tformat

        tdeck.save()

        decklist = 'Mountain'
        tdeck.set_cards_from_text(decklist)

        self.assertEquals(tdeck.get_card_count(), 1)

    def test_deck_1mountain(self):
        cache.clear()
        tlh = TestLoadHelper()
        tlh.basics_loader()

        tformat = Format.objects.filter(format='Standard_2015-01-23').first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = tformat

        tdeck.save()

        decklist = '1 Mountain'
        tdeck.set_cards_from_text(decklist)

        self.assertEquals(tdeck.get_card_count(), 1)

    def test_deck_1xmountain(self):
        cache.clear()
        tlh = TestLoadHelper()
        tlh.basics_loader()

        tformat = Format.objects.filter(format='Standard_2015-01-23').first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = tformat

        tdeck.save()

        decklist = '1x Mountain'
        tdeck.set_cards_from_text(decklist)

        self.assertEquals(tdeck.get_card_count(), 1)

    def test_deck_7mountain(self):
        cache.clear()
        tlh = TestLoadHelper()
        tlh.basics_loader()

        tformat = Format.objects.filter(format='Standard_2015-01-23').first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = tformat

        tdeck.save()

        decklist = '7 Mountain'
        tdeck.set_cards_from_text(decklist)

        self.assertEquals(tdeck.get_card_count(), 7)

        dcs = DeckCard.objects.filter(deck=tdeck)
        for dc in dcs:
            self.assertEquals(dc.cardcount, 7)
            self.assertEquals(dc.board, DeckCard.MAIN)
            self.assertEquals(dc.physicalcard.get_card_name(), 'Mountain')

    def test_deck_2cards(self):
        cache.clear()
        tlh = TestLoadHelper()
        tlh.basics_loader()

        tformat = Format.objects.filter(format='Standard_2015-01-23').first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = tformat

        tdeck.save()

        decklist = '''2 Mountain
4x Island'''
        tdeck.set_cards_from_text(decklist)

        self.assertEquals(tdeck.get_card_count(), 6)

        dcs = DeckCard.objects.filter(deck=tdeck).order_by('cardcount')
        dc = dcs[0]
        self.assertEquals(dc.cardcount, 2)
        self.assertEquals(dc.board, DeckCard.MAIN)
        self.assertEquals(dc.physicalcard.get_card_name(), 'Mountain')
        dc = dcs[1]
        self.assertEquals(dc.cardcount, 4)
        self.assertEquals(dc.board, DeckCard.MAIN)
        self.assertEquals(dc.physicalcard.get_card_name(), 'Island')

    def test_deck_emptylines(self):
        cache.clear()
        tlh = TestLoadHelper()
        tlh.basics_loader()

        tformat = Format.objects.filter(format='Standard_2015-01-23').first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = tformat

        tdeck.save()

        decklist = '''12 Mountain

4x Island
        '''
        tdeck.set_cards_from_text(decklist)

        self.assertEquals(tdeck.get_card_count(), 16)

    def test_deck_2cardssb(self):
        cache.clear()
        tlh = TestLoadHelper()
        tlh.basics_loader()

        tformat = Format.objects.filter(format='Standard_2015-01-23').first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = tformat

        tdeck.save()

        decklist = '''3 Mountain
sb: 4x Island'''
        tdeck.set_cards_from_text(decklist)

        self.assertEquals(tdeck.get_card_count(), 7)

    def test_deck_badname(self):
        cache.clear()
        tlh = TestLoadHelper()
        tlh.basics_loader()

        tformat = Format.objects.filter(format='Standard_2015-01-23').first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = tformat

        tdeck.save()

        decklist = '''3 Foo jib Battons'''
        try:
            tdeck.set_cards_from_text(decklist)
            self.assertTrue(False)
        except Deck.CardsNotFoundException as cnfes:
            self.assertEquals(cnfes.cnfes[0].text, 'Foo jib Battons'.lower())

        self.assertEquals(tdeck.get_card_count(), 0)

    def test_deck_badname_nosave(self):
        cache.clear()
        tlh = TestLoadHelper()
        tlh.basics_loader()

        tformat = Format.objects.filter(format='Standard_2015-01-23').first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = tformat

        tdeck.save()

        decklist = '''3 Mountain
sb: 4x Island'''
        tdeck.set_cards_from_text(decklist)

        self.assertEquals(tdeck.get_card_count(), 7)

        decklist = '''3 Foo jib Battons'''
        try:
            tdeck.set_cards_from_text(decklist)
            self.assertTrue(False)
        except Deck.CardsNotFoundException as cnfes:
            self.assertEquals(cnfes.cnfes[0].text, 'Foo jib Battons'.lower())

        self.assertEquals(tdeck.get_card_count(), 7)
