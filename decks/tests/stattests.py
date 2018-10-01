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
        myform = Format.objects.filter(formatname='Modern').order_by('-start_date').first()

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
        dc1.board = DeckCard.MAIN
        dc1.save()

        self.assertEquals(tdeck.get_card_count(), 60)

        tourny = Tournament(name='Test', url='http://foo.dog/', format=myform, start_date=myform.start_date, end_date=myform.start_date)
        tourny.save()
        #tourny = Tournament.objects.all().first()

        td = TournamentDeck(tournament=tourny, deck=tdeck, place=1)
        td.save()
        #td = TournamentDeck.objects.filter(tournament=tourny, deck=tdeck, place=1).first()

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
        myform = Format.objects.filter(formatname='Modern').order_by('-start_date').first()

        tourny = Tournament(name='Test', url='http://foo.dog/', format=myform, start_date=myform.start_date, end_date=myform.start_date)
        tourny.save()
        #tourny = Tournament.objects.all().first()

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
            dc1.board = DeckCard.MAIN
            dc1.save()

            td = TournamentDeck(tournament=tourny, deck=tdeck, place=incr)
            td.save()
            #td = TournamentDeck.objects.filter(tournament=tourny, deck=tdeck, place=incr).first()
            incr += 1

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
        myform = Format.objects.filter(formatname='Modern').order_by('-start_date').first()

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
        dc1.board = DeckCard.MAIN
        dc1.save()

        self.assertEquals(tdeck.get_card_count(), 60)

        tourny = Tournament(name='Test', url='http://foo.dog/', format=myform, start_date=myform.start_date, end_date=myform.start_date)
        tourny.save()
        #tourny = Tournament.objects.all().first()

        td = TournamentDeck(tournament=tourny, deck=tdeck, place=1)
        td.save()
        #td = TournamentDeck.objects.filter(tournament=tourny, deck=tdeck, place=1).first()

        FormatStat.calc_all()
        FormatCardStat.calc_all()

        fstat = FormatStat.objects.filter(format=myform).first()
        mstat = FormatCardStat.objects.filter(format=myform, physicalcard=mountain).first()

        dcount = mstat.deck_count
        self.assertEquals(dcount, 0)
        tdcount = fstat.tournamentdeck_count
        self.assertEquals(tdcount, 1, '1 Tournament Deck in the Format')

        self.assertEquals(mstat.in_decks_percentage(), 0.0, 'Mountain is in 0% of decks')

        self.assertEquals(mstat.occurence_count, 0, 'Mountain shows up 0 times in tournament decks')

        # the number of decks in this format that have this card
        self.assertEquals(mstat.deck_count, 0, '0 Tournament Decks have Mountain in the them')

        # the average card count when this card is included in a deck
        self.assertEquals(mstat.average_card_count_in_deck, 0.0, 'Average count of Mountain in Tournament Decks is 0')

        # the percentage of all cards in the format that are this card
        self.assertEquals(mstat.percentage_of_all_cards, 0.0, 'Average count of Tournament Decks with Mountain in it is 0')

        istat = FormatCardStat.objects.filter(format=myform, physicalcard=island).first()

        dcount = istat.deck_count
        self.assertEquals(dcount, 1, '1 Tournament Deck that has Island in it')
        self.assertEquals(istat.in_decks_percentage(), 100.0, 'Island is in 100% of decks')

        self.assertEquals(istat.occurence_count, 60, 'Island shows up 0 times in tournament decks')

        # the number of decks in this format that have this card
        self.assertEquals(istat.deck_count, 1, '1 Tournament Decks have Island in the them')

        # the average card count when this card is included in a deck
        self.assertEquals(istat.average_card_count_in_deck, 60.0, 'Average count of Island in Tournament Decks is 60')

        # the percentage of all cards in the format that are this card
        self.assertEquals(
            istat.percentage_of_all_cards,
            1.0,
            'Average count of Tournament Decks with Island in it should be 100, not {}'.format(
                istat.percentage_of_all_cards))

    def test_tcbf(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        mountain = BaseCard.objects.filter(name='Mountain').first().physicalcard
        island = BaseCard.objects.filter(name='Island').first().physicalcard
        formats = Format.objects.filter(formatname='Modern').order_by('-start_date')
        myform = formats[0]
        prev_form = formats[1]

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
        dc1.board = DeckCard.MAIN
        dc1.save()

        self.assertEquals(tdeck.get_card_count(), 60)

        tourny = Tournament(name='Test', url='http://foo.dog/', format=myform, start_date=myform.start_date, end_date=myform.start_date)
        tourny.save()

        td = TournamentDeck(tournament=tourny, deck=tdeck, place=1)
        td.save()

        FormatStat.calc_all()
        FormatCardStat.calc_all()

        fstat = FormatStat.objects.filter(format=myform).first()
        mstat = FormatCardStat.objects.filter(format=myform, physicalcard=mountain).first()
        istat = FormatCardStat.objects.filter(format=myform, physicalcard=island).first()

        cc = FormatCardStat.objects.top_cards_by_format(myform)
        self.assertEquals(cc.count(), 5, "5 cards, the basic lands, are all in this format")
        first_cc = cc.first()
        self.assertEquals(first_cc.physicalcard, island, "Top card in this format is Island")
        self.assertEquals(
            first_cc.previous_format_ids, str(
                prev_form.pk), "The previous format ids on the FormatCardStat object should be the previous format id")
        self.assertIsNone(first_cc.percentage_of_all_cards_previous(), 'None previously, so no number is returned')
        self.assertEquals(
            first_cc.percentage_of_all_cards_delta(),
            1.0,
            'There has been a change that is positive {}'.format(
                first_cc.percentage_of_all_cards_delta()))
        self.assertIsNone(first_cc.percentage_of_all_cards_perchange(), 'None previously, so no number is returned')

    def test_tcbf_2(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        mountain = BaseCard.objects.filter(name='Mountain').first().physicalcard
        island = BaseCard.objects.filter(name='Island').first().physicalcard
        formats = Format.objects.filter(formatname='Modern').order_by('-start_date')
        myform = formats[0]
        prev_form = formats[1]

        for fformat in [myform, prev_form]:
            tdeck = Deck()
            tdeck.name = 'My Deck Name in {}'.format(fformat.format)
            tdeck.url = 'http://card.ninja/{}'.format(fformat.id)
            tdeck.visibility = tdeck.VISIBLE
            tdeck.authorname = 'Test Dude'
            tdeck.format = fformat

            tdeck.save()
            tdeck = Deck.objects.get(pk=tdeck.id)

            dc1 = DeckCard()
            dc1.physicalcard = island
            dc1.deck = tdeck
            dc1.cardcount = 60
            dc1.board = DeckCard.MAIN
            dc1.save()

            tourny = Tournament(
                name='Test {}'.format(
                    fformat.pk),
                url='http://foo.dog/',
                format=fformat,
                start_date=fformat.start_date,
                end_date=fformat.start_date)
            tourny.save()

            td = TournamentDeck(tournament=tourny, deck=tdeck, place=1)
            td.save()

        FormatStat.calc_all()
        FormatCardStat.calc_all()

        fstat = FormatStat.objects.filter(format=myform).first()
        mstat = FormatCardStat.objects.filter(format=myform, physicalcard=mountain).first()

        cc = FormatCardStat.objects.top_cards_by_format(myform)
        first_cc = cc.first()
        self.assertEquals(first_cc.physicalcard, island, "Top card in this format is Island")
        self.assertEquals(
            first_cc.previous_format_ids, str(
                prev_form.pk), "The previous format ids on the FormatCardStat object should be the previous format id")
        self.assertEquals(first_cc.percentage_of_all_cards_previous(), 1.0, 'All previously, so 100% is returned')
        self.assertEquals(first_cc.percentage_of_all_cards_delta(), 0.0, 'Same as last format, so no delta')
        self.assertEquals(first_cc.percentage_of_all_cards_perchange(), 0.0, 'No change... still 100%')

    def test_tcbf_2b(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        mountain = BaseCard.objects.filter(name='Mountain').first().physicalcard
        island = BaseCard.objects.filter(name='Island').first().physicalcard
        formats = Format.objects.filter(formatname='Modern').order_by('-start_date')
        myform = formats[0]
        prev_form = formats[1]

        for fformat in [myform, prev_form]:
            tdeck = Deck()
            tdeck.name = 'My Deck Name in {}'.format(fformat.format)
            tdeck.url = 'http://card.ninja/{}'.format(fformat.id)
            tdeck.visibility = tdeck.VISIBLE
            tdeck.authorname = 'Test Dude'
            tdeck.format = fformat

            tdeck.save()
            tdeck = Deck.objects.get(pk=tdeck.id)

            dc1 = DeckCard()
            dc1.physicalcard = island
            dc1.deck = tdeck
            dc1.cardcount = 60
            dc1.board = DeckCard.MAIN
            dc1.save()

            tourny = Tournament(
                name='Test {}'.format(
                    fformat.pk),
                url='http://foo.dog/',
                format=fformat,
                start_date=fformat.start_date,
                end_date=fformat.start_date)
            tourny.save()

            td = TournamentDeck(tournament=tourny, deck=tdeck, place=1)
            td.save()

        FormatStat.calc_all()
        FormatCardStat.calc_all()

        fstat = FormatStat.objects.filter(format=myform).first()
        mstat = FormatCardStat.objects.filter(format=myform, physicalcard=mountain).first()
        istat = FormatCardStat.objects.filter(format=myform, physicalcard=island).first()

        first_cc = istat
        self.assertEquals(first_cc.percentage_of_all_cards_previous(), 1.0, 'All previously, so 100% is returned')
        self.assertEquals(first_cc.percentage_of_all_cards_delta(), 0.0, 'Same as last format, so no delta')
        self.assertEquals(first_cc.percentage_of_all_cards_perchange(), 0.0, 'No change... still 100%')

        self.assertEquals(first_cc.percentage_of_all_cards_previous(format_lookback_days=10), 1.0, 'F All previously, so 100% is returned')
        self.assertEquals(first_cc.percentage_of_all_cards_delta(format_lookback_days=10), 0.0, 'F Same as last format, so no delta')
        self.assertEquals(first_cc.percentage_of_all_cards_perchange(format_lookback_days=10), 0.0, 'F No change... still 100%')

    def test_tcbf_3(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        mountain = BaseCard.objects.filter(name='Mountain').first().physicalcard
        island = BaseCard.objects.filter(name='Island').first().physicalcard
        formats = Format.objects.filter(formatname='Modern').order_by('-start_date')
        myform = formats[0]
        prev_form = formats[1]

        # current format, all islands
        tdeck = Deck()
        tdeck.name = 'My Deck Name in {}'.format(myform.format)
        tdeck.url = 'http://card.ninja/{}'.format(myform.id)
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = myform

        tdeck.save()

        dc1 = DeckCard()
        dc1.physicalcard = island
        dc1.deck = tdeck
        dc1.cardcount = 60
        dc1.board = DeckCard.MAIN
        dc1.save()

        tourny = Tournament(name='Test {}'.format(myform.pk), url='http://foo.dog/', format=myform,
                            start_date=myform.start_date, end_date=myform.start_date)
        tourny.save()

        td = TournamentDeck(tournament=tourny, deck=tdeck, place=1)
        td.save()

        # previous format, half islands, hald mountains
        tdeck = Deck()
        tdeck.name = 'My Deck Name in {}'.format(prev_form.format)
        tdeck.url = 'http://card.ninja/{}'.format(prev_form.id)
        tdeck.visibility = tdeck.VISIBLE
        tdeck.authorname = 'Test Dude'
        tdeck.format = prev_form

        tdeck.save()

        dc1 = DeckCard()
        dc1.physicalcard = island
        dc1.deck = tdeck
        dc1.cardcount = 30
        dc1.board = DeckCard.MAIN
        dc1.save()
        dc2 = DeckCard()
        dc2.physicalcard = mountain
        dc2.deck = tdeck
        dc2.cardcount = 30
        dc2.board = DeckCard.MAIN
        dc2.save()

        tourny = Tournament(name='Test {}'.format(prev_form.pk), url='http://foo.dog/', format=prev_form,
                            start_date=prev_form.start_date, end_date=prev_form.start_date)
        tourny.save()

        td = TournamentDeck(tournament=tourny, deck=tdeck, place=1)
        td.save()

        FormatStat.calc_all()
        FormatCardStat.calc_all()

        fstat = FormatStat.objects.filter(format=myform).first()
        mstat = FormatCardStat.objects.filter(format=myform, physicalcard=mountain).first()
        istat = FormatCardStat.objects.filter(format=myform, physicalcard=island).first()

        cc = FormatCardStat.objects.top_cards_by_format(myform)
        first_cc = cc[0]
        self.assertEquals(first_cc.physicalcard, island, "Top card in this format is Island")
        self.assertEquals(first_cc.previous_format_ids, str(prev_form.pk),
                          "The previous format ids on the FormatCardStat object should be the previous format id")
        self.assertEquals(
            first_cc.percentage_of_all_cards_previous(),
            0.5,
            'Last format was split Islands and Mountains, so 50% is returned')
        self.assertEquals(first_cc.percentage_of_all_cards_delta(), 0.5, '50% points higher, so positive .5 is returned')
        self.assertEquals(first_cc.percentage_of_all_cards_perchange(),
                          1.0,
                          '100% change for Island - it doubled! Not {}'.format(first_cc.percentage_of_all_cards_perchange()))
        looked_at_mountain = False
        for other_cc in cc:
            if other_cc.physicalcard_id == mountain.id:
                looked_at_mountain = True
                self.assertEquals(other_cc.previous_format_ids, str(prev_form.pk),
                                  "The previous format ids on the FormatCardStat object should be the previous format id")
                self.assertEquals(
                    other_cc.percentage_of_all_cards_previous(),
                    0.5,
                    'Last format was split Islands and Mountains, so 50% is returned')
                self.assertEquals(other_cc.percentage_of_all_cards_delta(), -0.5, '50% points lower, so negative .5 is returned')
                self.assertEquals(other_cc.percentage_of_all_cards_perchange(), -
                                  1.0, '100% change for Mountain - big loss! Not {}'.format(other_cc.percentage_of_all_cards_perchange()))
        self.assertIs(looked_at_mountain, True, 'Why did we not look at Mountain?')

    def test_tcbf_4(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        mountain = BaseCard.objects.filter(name='Mountain').first().physicalcard
        island = BaseCard.objects.filter(name='Island').first().physicalcard
        swamp = BaseCard.objects.filter(name='Swamp').first().physicalcard
        plains = BaseCard.objects.filter(name='Plains').first().physicalcard
        formats = Format.objects.filter(formatname='Modern').order_by('-start_date')
        myform = formats[0]
        prev_form = formats[1]
        old_form = formats[2]

        # current format, all islands
        tourny = Tournament(name='Test {}'.format(myform.pk), url='http://foo.dog/', format=myform,
                            start_date=myform.start_date, end_date=myform.start_date)
        tourny.save()
        for dcc in range(0, 3):
            tdeck = Deck()
            tdeck.name = 'My {} Deck Name in {}'.format(dcc, myform.format)
            tdeck.url = 'http://card.ninja/{}'.format(myform.id)
            tdeck.visibility = tdeck.VISIBLE
            tdeck.authorname = 'Test Dude'
            tdeck.format = myform

            tdeck.save()

            dc1 = DeckCard()
            dc1.physicalcard = island
            dc1.deck = tdeck
            dc1.cardcount = 60
            dc1.board = DeckCard.MAIN
            dc1.save()

            td = TournamentDeck(tournament=tourny, deck=tdeck, place=dcc)
            td.save()

        # previous format, 10 islands, 20 swamps, 30 mountains
        tourny = Tournament(name='Test {}'.format(prev_form.pk), url='http://foo.dog/', format=prev_form,
                            start_date=prev_form.start_date, end_date=prev_form.start_date)
        tourny.save()
        for dcc in range(0, 3):
            tdeck = Deck()
            tdeck.name = 'My Deck Name in {}'.format(prev_form.format)
            tdeck.url = 'http://card.ninja/{}'.format(prev_form.id)
            tdeck.visibility = tdeck.VISIBLE
            tdeck.authorname = 'Test Dude'
            tdeck.format = prev_form

            tdeck.save()

            dc1 = DeckCard(physicalcard=island, deck=tdeck, cardcount=10, board=DeckCard.MAIN)
            dc1.save()
            dc2 = DeckCard(physicalcard=swamp, deck=tdeck, cardcount=20, board=DeckCard.MAIN)
            dc2.save()
            dc3 = DeckCard(physicalcard=mountain, deck=tdeck, cardcount=30, board=DeckCard.MAIN)
            dc3.save()

            td = TournamentDeck(tournament=tourny, deck=tdeck, place=dcc)
            td.save()

        # older format, 10 islands, 20 swamps, 30 mountains
        tourny = Tournament(name='Test {}'.format(old_form.pk), url='http://foo.dog/', format=old_form,
                            start_date=old_form.start_date, end_date=old_form.start_date)
        tourny.save()
        for dcc in range(0, 3):
            tdeck = Deck()
            tdeck.name = 'My {} Deck Name in {}'.format(dcc, old_form.format)
            tdeck.url = 'http://card.ninja/{}-{}'.format(old_form.id, dcc)
            tdeck.visibility = tdeck.VISIBLE
            tdeck.authorname = 'Test Dude'
            tdeck.format = old_form
            tdeck.save()

            dc1 = DeckCard(physicalcard=island, deck=tdeck, cardcount=10, board=DeckCard.MAIN)
            dc1.save()
            dc2 = DeckCard(physicalcard=swamp, deck=tdeck, cardcount=20, board=DeckCard.MAIN)
            dc2.save()
            dc3 = DeckCard(physicalcard=mountain, deck=tdeck, cardcount=30, board=DeckCard.MAIN)
            dc3.save()

            td = TournamentDeck(tournament=tourny, deck=tdeck, place=dcc)
            td.save()

        FormatStat.calc_all()
        FormatCardStat.calc_all()

        fstat = FormatStat.objects.filter(format=myform).first()
        mstat = FormatCardStat.objects.filter(format=myform, physicalcard=mountain).first()
        istat = FormatCardStat.objects.filter(format=myform, physicalcard=island).first()
        sstat = FormatCardStat.objects.filter(format=myform, physicalcard=swamp).first()

        # Try it once with looking back ONLY 1 format, and then again looking back 2 formats
        for lookback_days in (10, 40):  # note the test data has Modern formats ever month
            cc = FormatCardStat.objects.top_cards_by_format(myform, format_lookback_days=lookback_days)
            first_cc = cc[0]
            self.assertEquals(first_cc.physicalcard, island, "Top card in this format is Island")
            self.assertIs(
                str(
                    prev_form.pk) in first_cc.previous_format_ids,
                True,
                "The previous format ids on the FormatCardStat object should be the previous format id. Not {}".format(
                    first_cc.previous_format_ids))
            if lookback_days == 40:
                self.assertIs(
                    str(
                        old_form.pk) in first_cc.previous_format_ids,
                    True,
                    "The old format ids on the FormatCardStat object should be the old format id Not {}".format(
                        first_cc.previous_format_ids))

            self.assertAlmostEqual(
                first_cc.percentage_of_all_cards_previous(),
                1.0 / 6.0,
                msg='Last format was split Islands and Mountains, so 16.66% is returned')
            self.assertAlmostEqual(first_cc.percentage_of_all_cards_delta(),
                                   1.0 - (1.0 / 6.0),
                                   msg='83.33% points higher, so positive .8333 is returned')
            self.assertAlmostEqual(first_cc.percentage_of_all_cards_perchange(),
                                   5.0,
                                   msg='500% change for Island - it is big! Not {}'.format(first_cc.percentage_of_all_cards_perchange()))

            looked_at_mountain = False
            looked_at_swamp = False
            looked_at_plains = False
            for other_cc in cc:
                if other_cc.physicalcard_id == mountain.id:
                    looked_at_mountain = True
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_previous(), 0.5,
                                           msg='Last format was split Islands and Mountains, so 50% is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_delta(), -0.5,
                                           msg='50% points lower, so negative .5 is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_perchange(), -1.0,
                                           msg='100% change for Mountain - big loss! Not {}'.format(
                        other_cc.percentage_of_all_cards_perchange()))
                if other_cc.physicalcard_id == swamp.id:
                    looked_at_swamp = True
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_previous(), 1.0 / 3.0,
                                           msg='Last format had Swamps, Mountains, and Islands, so 33.3% is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_delta(), -1.0 / 3.0,
                                           msg='33.3% points lower, so negative .333 is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_perchange(), -1.0,
                                           msg='100% change for Swamp - big loss! Not {}'.format(
                        other_cc.percentage_of_all_cards_perchange()))
                if other_cc.physicalcard_id == plains.id:
                    looked_at_plains = True
                    self.assertAlmostEqual(
                        other_cc.percentage_of_all_cards_previous(),
                        0.0,
                        msg='Last format had Swamps, Mountains, and Islands, so 0% Plains should be returned, not {}'.format(
                            other_cc.percentage_of_all_cards_previous()))
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_delta(), 0.0,
                                           msg='No change for plains, so 0.0 is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_perchange(), 0.0,
                                           msg='0% change for Plains - oh well! Not {}'.format(
                                               other_cc.percentage_of_all_cards_perchange()))
            self.assertIs(looked_at_mountain, True, 'Why did we not look at Mountain?')
            self.assertIs(looked_at_swamp, True, 'Why did we not look at Swamp?')
            self.assertIs(looked_at_plains, True, 'Why did we not look at Plains?')

    def test_tcbf_5(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        mountain = BaseCard.objects.filter(name='Mountain').first().physicalcard
        island = BaseCard.objects.filter(name='Island').first().physicalcard
        swamp = BaseCard.objects.filter(name='Swamp').first().physicalcard
        plains = BaseCard.objects.filter(name='Plains').first().physicalcard
        formats = Format.objects.filter(formatname='Modern').order_by('-start_date')
        myform = formats[0]
        prev_form = formats[1]
        old_form = formats[2]

        # current format, all islands
        tourny = Tournament(name='Test {}'.format(myform.pk), url='http://foo.dog/', format=myform,
                            start_date=myform.start_date, end_date=myform.start_date)
        tourny.save()
        for dcc in range(0, 6):
            tdeck = Deck()
            tdeck.name = 'My {} Deck Name in {}'.format(dcc, myform.format)
            tdeck.url = 'http://card.ninja/{}'.format(myform.id)
            tdeck.visibility = tdeck.VISIBLE
            tdeck.authorname = 'Test Dude'
            tdeck.format = myform

            tdeck.save()

            dc1 = DeckCard(physicalcard=island, deck=tdeck, cardcount=31, board=DeckCard.MAIN)
            dc1.save()
            dc2 = DeckCard(physicalcard=swamp, deck=tdeck, cardcount=29, board=DeckCard.MAIN)
            dc2.save()

            td = TournamentDeck(tournament=tourny, deck=tdeck, place=dcc)
            td.save()

        # previous format, 10 islands, 20 swamps, 30 mountains
        tourny = Tournament(name='Test {}'.format(prev_form.pk), url='http://foo.dog/', format=prev_form,
                            start_date=prev_form.start_date, end_date=prev_form.start_date)
        tourny.save()
        for dcc in range(0, 6):
            tdeck = Deck()
            tdeck.name = 'My Deck Name in {}'.format(prev_form.format)
            tdeck.url = 'http://card.ninja/{}'.format(prev_form.id)
            tdeck.visibility = tdeck.VISIBLE
            tdeck.authorname = 'Test Dude'
            tdeck.format = prev_form

            tdeck.save()

            dc1 = DeckCard(physicalcard=island, deck=tdeck, cardcount=10, board=DeckCard.MAIN)
            dc1.save()
            dc2 = DeckCard(physicalcard=swamp, deck=tdeck, cardcount=20, board=DeckCard.MAIN)
            dc2.save()
            dc3 = DeckCard(physicalcard=mountain, deck=tdeck, cardcount=30, board=DeckCard.MAIN)
            dc3.save()

            td = TournamentDeck(tournament=tourny, deck=tdeck, place=dcc)
            td.save()

        # older format, 10 islands, 10 swamps, 10 mountains, 30 plains
        tourny = Tournament(name='Test {}'.format(old_form.pk), url='http://foo.dog/', format=old_form,
                            start_date=old_form.start_date, end_date=old_form.start_date)
        tourny.save()
        for dcc in range(0, 3):
            tdeck = Deck()
            tdeck.name = 'My {} Deck Name in {}'.format(dcc, old_form.format)
            tdeck.url = 'http://card.ninja/{}-{}'.format(old_form.id, dcc)
            tdeck.visibility = tdeck.VISIBLE
            tdeck.authorname = 'Test Dude'
            tdeck.format = old_form
            tdeck.save()

            dc1 = DeckCard(physicalcard=island, deck=tdeck, cardcount=10, board=DeckCard.MAIN)
            dc1.save()
            dc2 = DeckCard(physicalcard=swamp, deck=tdeck, cardcount=10, board=DeckCard.MAIN)
            dc2.save()
            dc3 = DeckCard(physicalcard=mountain, deck=tdeck, cardcount=10, board=DeckCard.MAIN)
            dc3.save()
            dc4 = DeckCard(physicalcard=plains, deck=tdeck, cardcount=30, board=DeckCard.MAIN)
            dc4.save()

            td = TournamentDeck(tournament=tourny, deck=tdeck, place=dcc)
            td.save()

        FormatStat.calc_all()
        FormatCardStat.calc_all()

        fstat = FormatStat.objects.filter(format=myform).first()
        mstat = FormatCardStat.objects.filter(format=myform, physicalcard=mountain).first()
        istat = FormatCardStat.objects.filter(format=myform, physicalcard=island).first()
        sstat = FormatCardStat.objects.filter(format=myform, physicalcard=swamp).first()

        # Try it once with looking back ONLY 1 format, and then again looking back 2 formats
        for lookback_days in (10,):
            cc = FormatCardStat.objects.top_cards_by_format(myform, format_lookback_days=lookback_days)
            first_cc = cc[0]
            self.assertEquals(first_cc.physicalcard, island, "Top card in this format is Island")
            self.assertIs(
                str(
                    prev_form.pk) in first_cc.previous_format_ids,
                True,
                "The previous format ids on the FormatCardStat object should be the previous format id. Not {}".format(
                    first_cc.previous_format_ids))
            if lookback_days == 40:
                self.assertIs(
                    str(
                        old_form.pk) in first_cc.previous_format_ids,
                    True,
                    "The old format ids on the FormatCardStat object should be the old format id Not {}".format(
                        first_cc.previous_format_ids))

            # in prev_format, 1 out of 6 were Island
            self.assertAlmostEqual(
                first_cc.percentage_of_all_cards_previous(),
                1.0 / 6.0,
                msg='Last format was split 1 out of 6 were Islands, so 16.66% is returned')
            # Now Island is 31/60, so 31/60 - 10/60 = 35%
            self.assertAlmostEqual(first_cc.percentage_of_all_cards_delta(),
                                   (31.0 / 60.0) - (10.0 / 60.0),
                                   msg='35.0% points higher, so positive .35 is returned')
            self.assertAlmostEqual(first_cc.percentage_of_all_cards_perchange(),
                                   0.35 / (1.0 / 6.0),
                                   msg='210% change for Island - it is big! Not {}'.format(first_cc.percentage_of_all_cards_perchange()))

            looked_at_mountain = False
            looked_at_swamp = False
            looked_at_plains = False
            for other_cc in cc:
                if other_cc.physicalcard_id == mountain.id:
                    looked_at_mountain = True
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_previous(), 0.5,
                                           msg='Last format was split Islands and Mountains, so 50% is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_delta(), -0.5,
                                           msg='50% points lower, so negative .5 is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_perchange(), -1.0,
                                           msg='100% change for Mountain - big loss! Not {}'.format(
                        other_cc.percentage_of_all_cards_perchange()))
                if other_cc.physicalcard_id == swamp.id:
                    looked_at_swamp = True
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_previous(), 1.0 / 3.0,
                                           msg='Last format had Swamps, Mountains, and Islands, so 33.3% is returned')
                    # had been a 1/3, and now 29/60th
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_delta(), (29.0 / 60.0) - (1.0 / 3.0),
                                           msg='15% points higher, so negative .15 is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_perchange(), 0.45,
                                           msg='45% change for Swamp - big win! Not {}'.format(
                        other_cc.percentage_of_all_cards_perchange()))
                if other_cc.physicalcard_id == plains.id:
                    looked_at_plains = True
                    self.assertAlmostEqual(
                        other_cc.percentage_of_all_cards_previous(),
                        0.0,
                        msg='Last format had Swamps, Mountains, and Islands, so 0% Plains should be returned, not {}'.format(
                            other_cc.percentage_of_all_cards_previous()))
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_delta(), 0.0,
                                           msg='No change for plains, so 0.0 is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_perchange(), 0.0,
                                           msg='0% change for Plains - oh well! Not {}'.format(
                                               other_cc.percentage_of_all_cards_perchange()))
            self.assertIs(looked_at_mountain, True, 'Why did we not look at Mountain?')
            self.assertIs(looked_at_swamp, True, 'Why did we not look at Swamp?')
            self.assertIs(looked_at_plains, True, 'Why did we not look at Plains?')

        for lookback_days in (40,):  # look back 2 formats now!!
            cc = FormatCardStat.objects.top_cards_by_format(myform, format_lookback_days=lookback_days)
            first_cc = cc[0]
            self.assertEquals(first_cc.physicalcard, island, "Top card in this format is Island")
            self.assertIs(
                str(
                    prev_form.pk) in first_cc.previous_format_ids,
                True,
                "The previous format ids on the FormatCardStat object should be the previous format id. Not {}".format(
                    first_cc.previous_format_ids))
            self.assertIs(str(old_form.pk) in first_cc.previous_format_ids,
                          True,
                          "The old format ids on the FormatCardStat object should be the old format id Not {}".format(first_cc.previous_format_ids))

            # in prev_format, 1 out of 6 were Island
            self.assertAlmostEqual(
                first_cc.percentage_of_all_cards_previous(),
                1.0 / 6.0,
                msg='Last 2 formats summed was split 1 out of 6 were Islands, so 16.66% is returned')
            # Now Island is 31/60, so 31/60 - 10/60 = 35%
            self.assertAlmostEqual(first_cc.percentage_of_all_cards_delta(),
                                   (31.0 / 60.0) - (10.0 / 60.0),
                                   msg='35.0% points higher, so positive .35 is returned')
            self.assertAlmostEqual(first_cc.percentage_of_all_cards_perchange(),
                                   0.35 / (1.0 / 6.0),
                                   msg='210% change for Island - it is big! Not {}'.format(first_cc.percentage_of_all_cards_perchange()))

            looked_at_mountain = False
            looked_at_swamp = False
            looked_at_plains = False
            for other_cc in cc:
                if other_cc.physicalcard_id == mountain.id:
                    looked_at_mountain = True
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_previous(), 21.0 / 54.0,
                                           msg='Last formats had 210 Mountains out of 540 cards, so 38.8% is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_delta(), -21.0 / 54.0,
                                           msg='38.8% points lower, so negative .388 is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_perchange(), -1.0,
                                           msg='100% change for Mountain - big loss! Not {}'.format(
                        other_cc.percentage_of_all_cards_perchange()))
                if other_cc.physicalcard_id == swamp.id:
                    looked_at_swamp = True
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_previous(), 5.0 / 18.0,
                                           msg='Last formats 5 out of 18 cards as Swamps, so 27.7% is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_delta(), 29.0 / 60.0 - 5.0 / 18.0,
                                           msg='20.6% points better, so positive .2066 is returned')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_perchange(), (29.0 / 60.0 - 5.0 / 18.0) / (5.0 / 18.0),
                                           msg='74% change for Swamp - big win! Not {}'.format(
                        other_cc.percentage_of_all_cards_perchange()))
                if other_cc.physicalcard_id == plains.id:
                    looked_at_plains = True
                    self.assertAlmostEqual(
                        other_cc.percentage_of_all_cards_previous(),
                        1.0 / 6.0,
                        msg='Last formats had some Plains, so 16.6% Plains should be returned, not {}'.format(
                            other_cc.percentage_of_all_cards_previous()))
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_delta(), -1.0 / 6.0,
                                           msg='All Plains are gone, so delta is negative .1666')
                    self.assertAlmostEqual(other_cc.percentage_of_all_cards_perchange(), -1.0,
                                           msg='-100% change for Plains - oh well! Not {}'.format(
                                               other_cc.percentage_of_all_cards_perchange()))
            self.assertIs(looked_at_mountain, True, 'Why did we not look at Mountain?')
            self.assertIs(looked_at_swamp, True, 'Why did we not look at Swamp?')
            self.assertIs(looked_at_plains, True, 'Why did we not look at Plains?')
