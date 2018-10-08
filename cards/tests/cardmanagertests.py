# -*- coding: utf-8 -*-

from django.test import TestCase
from cards.models import Format
from cards.models import Card
from cards.models import BaseCard
from cards.models import CardRating
from cards.models import FormatBasecard
from cards.models import CardManager
FormatNotSpecifiedException = CardManager.FormatNotSpecifiedException
from datetime import datetime
from django.core import management
import sys
err = sys.stderr


def setup():
    management.call_command('loaddata', 'mtgdbapp_testdata.json', verbosity=0)


def teardown():
    management.call_command('flush', verbosity=0, interactive=False)

# class CardManagerROTestCase(FastFixtureTestCase):


class CardManagerROTestCase(TestCase):
    #fixtures = ['mtgdbapp_testdata', ]

    def _fixture_setup(self):
        pass

    def _fixture_teardown(self):
        pass

    def test_all_cards_search(self):
        self.assertEquals(Card.objects.get_queryset().all().count(), 4189)
        allCards = Card.objects.get_queryset().all().order_by(
            'basecard__filing_name')
        first = allCards[0]
        self.assertEquals(first.basecard.filing_name, 'abandon hope')
        second = allCards[1]
        self.assertEquals(second.basecard.filing_name, 'abbey gargoyles')
        sixtythird = allCards[62]
        self.assertEquals(sixtythird.basecard.filing_name, 'aladdins lamp')

    def test_latest_printing(self):
        tower_qs = Card.playables.get_latest_printing().filter(
            basecard__filing_name__exact='urzas tower')
        self.assertEquals(tower_qs.count(), 1)
        self.assertEquals(tower_qs[0].basecard.name, 'Urza\'s Tower')
        self.assertEquals(tower_qs[0].multiverseid, 220958)

    def test_get_double_faced_card(self):
        delver_qs = Card.playables.get_latest_printing().filter(
            basecard__filing_name__exact='delver of secrets')
        self.assertEquals(delver_qs.count(), 1)
        self.assertEquals(delver_qs[0].basecard.name, 'Delver of Secrets')
        self.assertEquals(delver_qs[0].multiverseid, 226749)

    def test_standard_cards_sort_rating(self):
        format = Format.objects.get(pk=4)
        all_cards = Card.playables.get_queryset()
        allCards = Card.playables.in_cardrating_order(all_cards, format_id=format.id, sort_order=-1)
        first = allCards[0]
        self.assertEquals(first.basecard.name, 'Elspeth, Sun\'s Champion')
        self.assertEquals(first.basecard.id, 6004)
        self.assertGreaterEqual(
            first.basecard.physicalcard.get_cardratings(
                start_date=datetime(
                    2014, 10, 1), end_date=datetime(
                    2014, 10, 1)).filter(
                format_id=format.id).first().mu, allCards[1].basecard.physicalcard.get_cardratings(
                        start_date=datetime(
                            2014, 10, 1), end_date=datetime(
                                2014, 10, 1)).filter(
                                    format_id=format.id).first().mu)
        self.assertGreaterEqual(
            allCards[1].basecard.physicalcard.get_cardratings(
                start_date=datetime(
                    2014, 10, 1), end_date=datetime(
                    2014, 10, 1)).filter(
                format_id=format.id).first().mu, allCards[2].basecard.physicalcard.get_cardratings(
                        start_date=datetime(
                            2014, 10, 1), end_date=datetime(
                                2014, 10, 1)).filter(
                                    format_id=format.id).first().mu)
        self.assertGreaterEqual(
            allCards[2].basecard.physicalcard.get_cardratings(
                start_date=datetime(
                    2014, 10, 1), end_date=datetime(
                    2014, 10, 1)).filter(
                format_id=format.id).first().mu, allCards[3].basecard.physicalcard.get_cardratings(
                        start_date=datetime(
                            2014, 10, 1), end_date=datetime(
                                2014, 10, 1)).filter(
                                    format_id=format.id).first().mu)
        self.assertGreaterEqual(
            allCards[3].basecard.physicalcard.get_cardratings(
                start_date=datetime(
                    2014, 10, 1), end_date=datetime(
                    2014, 10, 1)).filter(
                format_id=format.id).first().mu, allCards[4].basecard.physicalcard.get_cardratings(
                        start_date=datetime(
                            2014, 10, 1), end_date=datetime(
                                2014, 10, 1)).filter(
                                    format_id=format.id).first().mu)
        self.assertGreaterEqual(
            allCards[4].basecard.physicalcard.get_cardratings(
                start_date=datetime(
                    2014, 10, 1), end_date=datetime(
                    2014, 10, 1)).filter(
                format_id=format.id).first().mu, allCards[5].basecard.physicalcard.get_cardratings(
                        start_date=datetime(
                            2014, 10, 1), end_date=datetime(
                                2014, 10, 1)).filter(
                                    format_id=format.id).first().mu)

    def test_modern_cards_sort_rating_desc(self):
        all_cards = Card.playables.get_queryset()
        allCards = Card.playables.in_cardrating_order(
            all_cards,
            format_id=1,
            sort_order=-1)
        first = allCards[0]
        self.assertEquals(first.basecard.name, 'Lightning Bolt')
        self.assertEquals(first.id, 68647)
        self.assertEquals(
            CardRating.objects.filter(physicalcard=first.basecard.physicalcard, format_id=1).first().mu,
            44.5023075558582)

    def test_modern_cards_sort_rating_asc(self):
        all_cards = Card.playables.get_queryset()
        allCards = Card.playables.in_cardrating_order(
            all_cards,
            format_id=1,
            sort_order=1)
        first = allCards[0]
        self.assertEquals(first.basecard.name, 'Abzan Charm')
        self.assertEquals(first.id, 64961)
        self.assertEquals(
            CardRating.objects.filter(physicalcard=first.basecard.physicalcard, format_id=1).first().mu,
            25)

    def test_modern_cards_name_term_sort_rating_desc(self):
        card_list = Card.playables.get_queryset().filter(
            basecard__filing_name__icontains='th')
        bc_vals = FormatBasecard.objects.filter(
            format__format__exact='Modern_2014-09-26').values_list('basecard', flat=True)
        card_list = card_list.filter(basecard__pk__in=bc_vals)
        cards = Card.playables.in_cardrating_order(
            card_list,
            format_id=1,
            sort_order=-1)
        first = cards[0]
        self.assertEquals(first.basecard.name, 'Path to Exile')
        self.assertEquals(first.basecard.id, 2047)
        self.assertEquals(
            CardRating.objects.filter(physicalcard=first.basecard.physicalcard, format_id=1).first().mu,
            34.0947162161112)


class CardTestCase(TestCase):
    #fixtures = ['mtgdbapp_testdata', ]

    def _fixture_setup(self):
        pass

    def _fixture_teardown(self):
        pass

    def test_get_double_faced_card(self):
        delver = Card.playables.get_latest_printing().filter(
            basecard__filing_name__exact='delver of secrets').first()
        self.assertEquals(delver.basecard.name, 'Delver of Secrets')
        aberration = delver.get_double_faced_card()
        self.assertIsNotNone(aberration)
        self.assertEquals(aberration.basecard.name, 'Insectile Aberration')
        self.assertEquals(
            delver.basecard.physicalcard.id,
            aberration.basecard.physicalcard.id)

    def test_get_double_faced_cardX(self):
        delver = Card.playables.get_latest_printing().filter(
            basecard__filing_name__exact='delver of secrets').first()
        self.assertEquals(delver.basecard.name, 'Delver of Secrets')
        self.assertEquals(delver, delver.get_first_card())
        self.assertEquals(delver.get_double_faced_card(), delver.get_second_card())

    def test_get_double_faced_card_reverse(self):
        aberration = Card.playables.get_latest_printing().filter(
            basecard__name__exact='Insectile Aberration').first()
        self.assertEquals(
            aberration.basecard.filing_name,
            'insectile aberration')
        #self.assertEquals(aberration.basecard.cmc, 0)
        # CMC for double-faced cards had a rules change!!
        # https://magic.wizards.com/en/articles/archive/feature/shadows-over-innistrad-mechanics
        self.assertEquals(aberration.basecard.cmc, 1)
        delver = aberration.get_double_faced_card()
        self.assertIsNotNone(delver)
        self.assertEquals(delver.basecard.name, 'Delver of Secrets')
        self.assertEquals(delver.basecard.cmc, 1)
        self.assertEquals(
            delver.basecard.physicalcard.id,
            aberration.basecard.physicalcard.id)

    def test_get_double_faced_card_reverseX(self):
        aberration = Card.playables.get_latest_printing().filter(
            basecard__name__exact='Insectile Aberration').first()
        self.assertEquals(aberration, aberration.get_second_card())
        self.assertEquals(aberration.get_double_faced_card(), aberration.get_first_card())

    def test_get_double_faced_card_not(self):
        mss = Card.playables.get_latest_printing().filter(
            basecard__filing_name__exact='monastery swiftspear').first()
        self.assertEquals(mss.basecard.name, 'Monastery Swiftspear')
        foo = mss.get_double_faced_card()
        self.assertIsNone(foo)

    def test_get_double_faced_card_notX(self):
        mss = Card.playables.get_latest_printing().filter(
            basecard__filing_name__exact='monastery swiftspear').first()
        self.assertEquals(mss.basecard.name, 'Monastery Swiftspear')
        foo = mss.get_first_card()
        self.assertEquals(mss, foo)
        bar = mss.get_second_card()
        self.assertIsNone(bar)

    def test_pcard_get_face_basecard0(self):
        startbc = BaseCard.objects.filter(cardposition=BaseCard.FRONT, name='Island').first()
        self.assertIsNotNone(startbc)
        pcard = startbc.physicalcard
        resultbc = pcard.get_face_basecard()
        self.assertEqual(resultbc.id, startbc.id)

    def test_pcard_get_face_basecard1(self):
        startbc = BaseCard.objects.filter(cardposition=BaseCard.FRONT, name='Delver of Secrets').first()
        self.assertIsNotNone(startbc)
        pcard = startbc.physicalcard
        resultbc = pcard.get_face_basecard()
        self.assertEqual(resultbc.id, startbc.id)

    def test_pcard_get_face_basecard2(self):
        startbc = BaseCard.objects.filter(name='Insectile Aberration').first()
        self.assertIsNotNone(startbc)
        pcard = startbc.physicalcard
        resultbc = pcard.get_face_basecard()
        self.assertNotEqual(resultbc.id, startbc.id)
        self.assertEqual(resultbc.physicalcard.id, startbc.physicalcard.id)

    def test_basecard_is_land0(self):
        startbc = BaseCard.objects.filter(cardposition=BaseCard.FRONT, name='Island').first()
        self.assertIsNotNone(startbc)
        self.assertTrue(startbc.is_land())

    def test_basecard_is_land1(self):
        startbc = BaseCard.objects.filter(cardposition=BaseCard.FRONT, name='Delver of Secrets').first()
        self.assertIsNotNone(startbc)
        self.assertFalse(startbc.is_land())

    def test_basecard_is_land2(self):
        startbc = BaseCard.objects.filter(name='Insectile Aberration').first()
        self.assertIsNotNone(startbc)
        self.assertFalse(startbc.is_land())

    def test_card_get_first_0(self):
        start_card = Card.objects.filter(basecard__cardposition=BaseCard.FRONT, basecard__name='Delver of Secrets').first()
        self.assertIsNotNone(start_card)
        start_id = start_card.id
        start_mvid = start_card.multiverseid
        start_name = start_card.basecard.name
        result_card = start_card.get_first_card()
        self.assertEqual(start_id, result_card.id)
        self.assertEqual(start_mvid, result_card.multiverseid)
        self.assertEqual(start_name, result_card.basecard.name)

    def test_card_get_first_1(self):
        start_card = Card.objects.filter(basecard__cardposition=BaseCard.FRONT, basecard__name='Plains').first()
        self.assertIsNotNone(start_card)
        start_id = start_card.id
        start_mvid = start_card.multiverseid
        start_name = start_card.basecard.name
        result_card = start_card.get_first_card()
        self.assertEqual(start_id, result_card.id)
        self.assertEqual(start_mvid, result_card.multiverseid)
        self.assertEqual(start_name, result_card.basecard.name)

    def test_card_get_first_2(self):
        start_card = Card.objects.filter(basecard__cardposition=BaseCard.BACK, basecard__name='Insectile Aberration').first()
        self.assertIsNotNone(start_card)
        start_id = start_card.id
        start_mvid = start_card.multiverseid
        start_name = start_card.basecard.name
        result_card = start_card.get_first_card()
        self.assertNotEqual(start_id, result_card.id)
        self.assertNotEqual(start_mvid, result_card.multiverseid)
        self.assertNotEqual(start_name, result_card.basecard.name)
        self.assertEqual(u'Delver of Secrets', result_card.basecard.name)

    def test_card_get_second_0(self):
        start_card = Card.objects.filter(basecard__cardposition=BaseCard.FRONT, basecard__name='Delver of Secrets').first()
        self.assertIsNotNone(start_card)
        start_id = start_card.id
        start_mvid = start_card.multiverseid
        start_name = start_card.basecard.name
        result_card = start_card.get_second_card()
        self.assertNotEqual(start_id, result_card.id)
        self.assertNotEqual(start_mvid, result_card.multiverseid)
        self.assertNotEqual(start_name, result_card.basecard.name)
        self.assertEqual(u'Insectile Aberration', result_card.basecard.name)

    def test_card_get_second_1(self):
        start_card = Card.objects.filter(basecard__cardposition=BaseCard.FRONT, basecard__name='Plains').first()
        self.assertIsNotNone(start_card)
        result_card = start_card.get_second_card()
        self.assertIsNone(result_card)

    def test_card_get_second_2(self):
        start_card = Card.objects.filter(basecard__cardposition=BaseCard.BACK, basecard__name='Insectile Aberration').first()
        self.assertIsNotNone(start_card)
        start_id = start_card.id
        start_mvid = start_card.multiverseid
        start_name = start_card.basecard.name
        result_card = start_card.get_second_card()
        self.assertEqual(start_id, result_card.id)
        self.assertEqual(start_mvid, result_card.multiverseid)
        self.assertEqual(start_name, result_card.basecard.name)

    def test_card_get_all_0(self):
        start_card = Card.objects.filter(basecard__cardposition=BaseCard.FRONT, basecard__name='Delver of Secrets').first()
        self.assertIsNotNone(start_card)
        result = start_card.get_all_cards()
        self.assertEqual(2, len(result))
        self.assertEqual(u'Delver of Secrets', result[0].basecard.name)
        self.assertEqual(u'Insectile Aberration', result[1].basecard.name)
        self.assertEqual(result[0].expansionset_id, result[1].expansionset_id)

    def test_card_get_all_1(self):
        start_card = Card.objects.filter(basecard__cardposition=BaseCard.BACK, basecard__name='Insectile Aberration').first()
        self.assertIsNotNone(start_card)
        result = start_card.get_all_cards()
        self.assertEqual(2, len(result))
        self.assertEqual(u'Delver of Secrets', result[0].basecard.name)
        self.assertEqual(u'Insectile Aberration', result[1].basecard.name)
        self.assertEqual(result[0].expansionset_id, result[1].expansionset_id)

    def test_card_get_all_2(self):
        start_card = Card.objects.filter(basecard__cardposition=BaseCard.FRONT, basecard__name='Swamp').first()
        self.assertIsNotNone(start_card)
        result = start_card.get_all_cards()
        self.assertEqual(2, len(result))
        self.assertEqual(u'Swamp', result[0].basecard.name)
        self.assertIsNone(result[1])
