from django.test import TestCase, TransactionTestCase
from django_nose import FastFixtureTestCase

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction

from datetime import datetime

from cards.models import PhysicalCard, Format, Color, BaseCard, Card
from decks.models import Deck, DeckCard

from cards.tests.helper import TestLoadHelper

import sys
err = sys.stderr


class DecksTestCase(TestCase):

    exempt_from_fixture_bundling = True

    def test_deck_inst(self):
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

        self.assertEquals(tdeck.format.id, tformat.id)

        c1 = Card.objects.filter(multiverseid=1002).first()
        self.assertEquals(c1.basecard.name, 'Island')

        dc1 = DeckCard()
        dc1.physicalcard = c1.basecard.physicalcard
        dc1.deck = tdeck
        dc1.cardcount = 8
        dc1.board = dc1.MAIN
        dc1.save()

        self.assertEquals(tdeck.get_card_count(), 8)

        c2 = Card.objects.filter(multiverseid=1004).first()
        self.assertEquals(c2.basecard.name, 'Mountain')

        dc2 = DeckCard()
        dc2.physicalcard = c2.basecard.physicalcard
        dc2.deck = tdeck
        dc2.cardcount = 3
        dc2.board = dc2.MAIN
        dc2.save()

        self.assertEquals(tdeck.get_card_count(), 11)

    def test_deck_60mountains(self):
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

        c1 = Card.objects.filter(multiverseid=1004).first()

        dc1 = DeckCard()
        dc1.physicalcard = c1.basecard.physicalcard
        dc1.deck = tdeck
        dc1.cardcount = 60
        dc1.board = dc1.MAIN
        dc1.save()

        self.assertEquals(tdeck.get_card_count(), 60)

        self.assertTrue(tdeck.is_legal())

    def test_deck_61mountains(self):
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

        c1 = Card.objects.filter(multiverseid=1004).first()

        dc1 = DeckCard()
        dc1.physicalcard = c1.basecard.physicalcard
        dc1.deck = tdeck
        dc1.cardcount = 61
        dc1.board = dc1.MAIN
        dc1.save()

        self.assertEquals(tdeck.get_card_count(), 61)

        self.assertTrue(tdeck.is_legal())

    def test_deck_59mountains(self):
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

        c1 = Card.objects.filter(multiverseid=1004).first()

        dc1 = DeckCard()
        dc1.physicalcard = c1.basecard.physicalcard
        dc1.deck = tdeck
        dc1.cardcount = 59
        dc1.board = dc1.MAIN
        dc1.save()

        self.assertEquals(tdeck.get_card_count(), 59)

        self.assertFalse(tdeck.is_legal())
