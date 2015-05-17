from django.test import TestCase, TransactionTestCase
from django_nose import FastFixtureTestCase

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction

from datetime import datetime

from cards.models import PhysicalCard, Format, Color, BaseCard, Card
from decks.models import Deck, DeckCard, FormatCardStat, Tournament, TournamentDeck, FormatStat

from cards.tests.helper import TestLoadHelper

import sys
err = sys.stderr


class FormatCardStatTestCase(TestCase):

    exempt_from_fixture_bundling = True

    FormatStat.MIN_DECKS_IN_TOURNAMENT = 0

    def test_empty(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        island = BaseCard.objects.filter(name='Island').first().physicalcard
        modern = Format.objects.all().first()

        FormatStat.calc_all()
        FormatCardStat.calc_all()

        fstat = FormatStat.objects.filter(format=modern).first()
        mstat = FormatCardStat.objects.filter(format=modern, physicalcard=island).first()
        dcount = mstat.deck_count
        self.assertEquals(dcount, 0)
        tdcount = fstat.tournamentdeck_count
        self.assertEquals(tdcount, 0)

    def test_one_deck(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        island = BaseCard.objects.filter(name='Island').first().physicalcard
        myform = Format.objects.all().first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = myform

        tdeck.save()
        tdeck = Deck.objects.get(pk=tdeck.id)

        dc1 = DeckCard()
        dc1.physicalcard = island
        dc1.deck = tdeck
        dc1.cardcount = 60
        dc1.board = dc1.MAIN
        dc1.save()

        self.assertEquals(tdeck.get_card_count(), 60)

        tourny = Tournament(name='Test', url='http://foo.dog/', format=myform, start_date='2015-04-01', end_date='2015-04-01')
        tourny.save()
        tourny = Tournament.objects.all().first()

        td = TournamentDeck(tournament=tourny, deck=tdeck, place=1)
        td.save()
        td = TournamentDeck.objects.filter(tournament=tourny, deck=dc1, place=1).first()

        FormatStat.calc_all()
        FormatCardStat.calc_all()

        fstat = FormatStat.objects.filter(format=myform).first()
        mstat = FormatCardStat.objects.filter(format=myform, physicalcard=island).first()
        dcount = mstat.deck_count
        self.assertEquals(dcount, 1)
        tdcount = fstat.tournamentdeck_count
        self.assertEquals(tdcount, 1)

        tdccount = fstat.tournamentdeckcard_count
        self.assertEquals(tdccount, 60)

        self.assertEquals(mstat.in_decks_percentage(), 100.0)

    def test_two_decks(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        plains = BaseCard.objects.filter(name='Plains').first().physicalcard
        island = BaseCard.objects.filter(name='Island').first().physicalcard
        myform = Format.objects.all().first()

        tourny = Tournament(name='Test', url='http://foo.dog/', format=myform, start_date='2015-04-01', end_date='2015-04-01')
        tourny.save()
        tourny = Tournament.objects.all().first()

        incr = 1
        for pcard in [plains, island]:
            tdeck = Deck()
            tdeck.name = 'My Deck Name'
            tdeck.url = 'http://card.ninja/'
            tdeck.visibility = tdeck.VISIBLE
            tdeck.authorname = 'Test Dude'
            tdeck.format = myform

            tdeck.save()
            tdeck = Deck.objects.get(pk=tdeck.id)

            dc1 = DeckCard()
            dc1.physicalcard = pcard
            dc1.deck = tdeck
            dc1.cardcount = 60
            dc1.board = dc1.MAIN
            dc1.save()

            td = TournamentDeck(tournament=tourny, deck=tdeck, place=incr)
            td.save()
            td = TournamentDeck.objects.filter(tournament=tourny, deck=dc1, place=incr).first()
            incr = incr + 1

        FormatStat.calc_all()
        FormatCardStat.calc_all()

        fstat = FormatStat.objects.filter(format=myform).first()
        mstat = FormatCardStat.objects.filter(format=myform, physicalcard=island).first()

        dcount = mstat.deck_count
        self.assertEquals(dcount, 1)
        tdcount = fstat.tournamentdeck_count
        self.assertEquals(tdcount, 2)

        self.assertEquals(mstat.in_decks_percentage(), 50.0)

    def test_one_deck_abs_card(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        mountain = BaseCard.objects.filter(name='Mountain').first().physicalcard
        island = BaseCard.objects.filter(name='Island').first().physicalcard
        myform = Format.objects.all().first()

        tdeck = Deck()
        tdeck.name = 'My Deck Name'
        tdeck.url = 'http://card.ninja/'
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = myform

        tdeck.save()
        tdeck = Deck.objects.get(pk=tdeck.id)

        dc1 = DeckCard()
        dc1.physicalcard = island
        dc1.deck = tdeck
        dc1.cardcount = 60
        dc1.board = dc1.MAIN
        dc1.save()

        self.assertEquals(tdeck.get_card_count(), 60)

        tourny = Tournament(name='Test', url='http://foo.dog/', format=myform, start_date='2015-04-01', end_date='2015-04-01')
        tourny.save()
        tourny = Tournament.objects.all().first()

        td = TournamentDeck(tournament=tourny, deck=tdeck, place=1)
        td.save()
        td = TournamentDeck.objects.filter(tournament=tourny, deck=dc1, place=1).first()

        FormatStat.calc_all()
        FormatCardStat.calc_all()

        fstat = FormatStat.objects.filter(format=myform).first()
        mstat = FormatCardStat.objects.filter(format=myform, physicalcard=mountain).first()

        dcount = mstat.deck_count
        self.assertEquals(dcount, 0)
        tdcount = fstat.tournamentdeck_count
        self.assertEquals(tdcount, 1)

        self.assertEquals(mstat.in_decks_percentage(), 0.0)
