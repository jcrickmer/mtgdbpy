# -*- coding: utf-8 -*-

from django.test import TestCase, TransactionTestCase
from django_nose import FastFixtureTestCase
from cards.models import Color, Rarity, Type, Subtype, PhysicalCard, Card, BaseCard, CardRating, ExpansionSet, FormatBasecard, SearchPredicate
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction
from cards.tests.helper import TestLoadHelper

import sys
err = sys.stderr

# Create your tests here.


class MigrationTestCase(TransactionTestCase):
    fixtures = ['mtgdbapp_testdata', ]
    serialized_rollback = True
    # def test_basic_addition(self):
    #	serialized_rollback = True
    #	self.assertEqual(1 + 1, 2)

    def test_colors(self):
        serialized_rollback = True
        white = Color.objects.get(pk='W')
        blue = Color.objects.get(pk='U')
        black = Color.objects.get(pk='B')
        red = Color.objects.get(pk='R')
        green = Color.objects.get(pk='G')
        colorless = Color.objects.get(pk='C')
        colors = Color.objects.all()
        self.assertEqual(len(colors), 6)

    def test_rarities(self):
        serialized_rollback = True
        b = Rarity.objects.get(pk='b')
        self.assertEqual(b.sortorder, 0)
        c = Rarity.objects.get(pk='c')
        self.assertEqual(c.sortorder, 1)
        u = Rarity.objects.get(pk='u')
        self.assertEqual(u.sortorder, 2)
        r = Rarity.objects.get(pk='r')
        self.assertEqual(r.sortorder, 3)
        m = Rarity.objects.get(pk='m')
        self.assertEqual(m.sortorder, 4)
        s = Rarity.objects.get(pk='s')
        self.assertEqual(s.sortorder, 5)
        rarities = Rarity.objects.all()
        self.assertEqual(len(rarities), 6)


class TypeTestCase(TestCase):

    def test_type_create_basic(self):
        testType_s = 'Contraption'
        t = Type()
        t.type = testType_s
        t.save()

        t1 = Type.objects.filter(type__exact=testType_s).first()
        self.assertEqual(t1.type, testType_s)

    def test_type_uniqueness(self):
        testType_s = 'Contraption'
        t = Type()
        t.type = testType_s
        t.save()

        t2 = Type()
        t2.type = testType_s
        self.assertRaises(IntegrityError, t2.save)


class SubtypeTestCase(TestCase):

    def test_subtype_create_basic(self):
        testSubtype_s = 'Alien'
        st = Subtype()
        st.subtype = testSubtype_s
        st.save()

        st1 = Subtype.objects.filter(subtype__exact=testSubtype_s).first()
        self.assertEqual(st1.subtype, testSubtype_s)

    def test_subtype_uniqueness(self):
        testSubtype_s = 'Alien'
        st = Subtype()
        st.subtype = testSubtype_s
        st.save()

        st2 = Subtype()
        st2.subtype = testSubtype_s
        self.assertRaises(IntegrityError, st2.save)


class PhysicalCardTestCase(TestCase):

    def test_physicalcard_create_basic(self):
        pc = PhysicalCard()
        self.assertIsNone(pc.id)
        pc.save()
        self.assertIsNotNone(pc.id)
        self.assertEquals(pc.layout, PhysicalCard.NORMAL)

        pc2 = PhysicalCard.objects.get(pk=pc.id)
        self.assertEqual(pc2.layout, pc.layout)

    def test_physicalcard_layout_choices(self):
        self.assertEquals(PhysicalCard.NORMAL, 'normal')
        self.assertEquals(PhysicalCard.SPLIT, 'split')
        self.assertEquals(PhysicalCard.FLIP, 'flip')
        self.assertEquals(PhysicalCard.DOUBLE, 'double-faced')
        self.assertEquals(PhysicalCard.TOKEN, 'token')
        self.assertEquals(PhysicalCard.PLANE, 'plane')
        self.assertEquals(PhysicalCard.SCHEME, 'scheme')
        self.assertEquals(PhysicalCard.PHENOMENON, 'phenomenon')
        self.assertEquals(PhysicalCard.LEVELER, 'leveler')
        self.assertEquals(PhysicalCard.VANGUARD, 'vanguard')

    def test_physicalcard_cardrating_none(self):
        pc = PhysicalCard()
        pc.save()

        self.assertRaises(
            CardRating.DoesNotExist,
            pc.get_cardrating,
            None,
            None)
        self.assertRaises(
            CardRating.DoesNotExist,
            pc.get_cardrating,
            35432,
            4652)


class BaseCardTestCase(TestCase):

    def test_basecard_create_basic(self):
        bc = BaseCard()
        self.assertIsNone(bc.id)
        with transaction.atomic():
            self.assertRaises(IntegrityError, bc.save)

        pc = PhysicalCard()
        pc.save()
        bc = BaseCard()
        bc.physicalcard = pc

        # Still not good enough. We require a name
        self.assertRaisesRegexp(
            ValidationError,
            'BaseCard must have a name',
            bc.clean)
        bc.name = 'Test Name'
        bc.clean()
        bc.save()
        self.assertIsNotNone(bc.id)
        self.assertEquals(bc.name, 'Test Name')
        self.assertEquals(bc.filing_name, 'test name')
        self.assertEquals(bc.rules_text, '')
        self.assertEquals(bc.mana_cost, '')
        self.assertEquals(bc.cmc, 0)
        self.assertIsNone(bc.power)
        self.assertIsNone(bc.toughness)
        self.assertIsNone(bc.loyalty)
        self.assertEquals(len(bc.get_rulings()), 0)
        # I REALLY DON'T LIKE THIS. REVISIT - Type is required. How do I
        # enforce this requirement?
        self.assertEquals(len(bc.types.all()), 0)
        self.assertEquals(len(bc.subtypes.all()), 0)
        # I REALLY DON'T LIKE THIS. REVISIT - Color is required. How do I
        # enforce this requirement?
        self.assertEquals(len(bc.colors.all()), 0)


class CardCreateTestCase(TestCase):

    def test_card_all_one_cards(self):
        self.assertEquals(Card.objects.get_queryset().all().count(), 0)

        # add expansion set
        es = ExpansionSet(name="Alpha", abbr="aaa")
        es.save()

        # add a rarity
        rc = Rarity(id='c', rarity='Common', sortorder=1)
        rc.save()

        # add a card
        pc = PhysicalCard()
        pc.save()
        bc = BaseCard()
        bc.physicalcard = pc

        bc.name = 'Test Name'
        bc.clean()
        bc.save()
        self.assertEquals(bc.physicalcard.layout, PhysicalCard.NORMAL)
        c = Card(
            basecard=bc,
            rarity=rc,
            expansionset=es,
            multiverseid=100,
            card_number='99')
        c.save()

        self.assertEquals(Card.objects.get_queryset().all().count(), 1)


# class CardManagerROTestCase(FastFixtureTestCase):
class CardManagerROTestCase(TestCase):
    fixtures = ['mtgdbapp_testdata', ]

    def test_all_cards_search(self):
        self.assertEquals(Card.objects.get_queryset().all().count(), 2015)
        allCards = Card.objects.get_queryset().all().order_by(
            'basecard__filing_name')
        first = allCards[0]
        self.assertEquals(first.basecard.filing_name, 'abrupt decay')
        second = allCards[1]
        self.assertEquals(second.basecard.filing_name, 'abzan charm')
        sixtythird = allCards[62]
        self.assertEquals(sixtythird.basecard.filing_name, 'bojuka bog')

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
        all_cards = Card.playables.get_queryset()
        allCards = Card.playables.in_cardrating_order(
            all_cards,
            format_id=4,
            test_id=1,
            sort_order=-
            1)
        first = allCards[0]
        self.assertEquals(first.basecard.name, 'Elspeth, Sun\'s Champion')
        self.assertEquals(first.basecard.id, 6004)
        self.assertGreaterEqual(
            first.basecard.physicalcard.get_cardrating(
                4, 1).mu, allCards[1].basecard.physicalcard.get_cardrating(
                4, 1).mu)
        self.assertGreaterEqual(
            allCards[1].basecard.physicalcard.get_cardrating(
                4, 1).mu, allCards[2].basecard.physicalcard.get_cardrating(
                4, 1).mu)
        self.assertGreaterEqual(
            allCards[2].basecard.physicalcard.get_cardrating(
                4, 1).mu, allCards[3].basecard.physicalcard.get_cardrating(
                4, 1).mu)
        self.assertGreaterEqual(
            allCards[3].basecard.physicalcard.get_cardrating(
                4, 1).mu, allCards[4].basecard.physicalcard.get_cardrating(
                4, 1).mu)
        self.assertGreaterEqual(
            allCards[4].basecard.physicalcard.get_cardrating(
                4, 1).mu, allCards[5].basecard.physicalcard.get_cardrating(
                4, 1).mu)

    def test_modern_cards_sort_rating_desc(self):
        all_cards = Card.playables.get_queryset()
        allCards = Card.playables.in_cardrating_order(
            all_cards,
            format_id=1,
            test_id=1,
            sort_order=-
            1)
        first = allCards[0]
        self.assertEquals(first.basecard.name, 'Lightning Bolt')
        self.assertEquals(first.id, 68647)
        self.assertEquals(
            first.basecard.physicalcard.get_cardrating(
                1,
                1).mu,
            44.5023075558582)

    def test_modern_cards_sort_rating_asc(self):
        all_cards = Card.playables.get_queryset()
        allCards = Card.playables.in_cardrating_order(
            all_cards,
            format_id=1,
            test_id=1,
            sort_order=1)
        first = allCards[0]
        self.assertEquals(first.basecard.name, 'Abzan Charm')
        self.assertEquals(first.id, 64961)
        self.assertEquals(
            first.basecard.physicalcard.get_cardrating(
                1,
                1).mu,
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
            test_id=1,
            sort_order=-1)
        first = cards[0]
        self.assertEquals(first.basecard.name, 'Path to Exile')
        self.assertEquals(first.basecard.id, 2047)
        self.assertEquals(
            first.basecard.physicalcard.get_cardrating(
                1,
                1).mu,
            34.0947162161112)


class CardTestCase(TestCase):
    fixtures = ['mtgdbapp_testdata', ]

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

    def test_get_double_faced_card_reverse(self):
        aberration = Card.playables.get_latest_printing().filter(
            basecard__name__exact='Insectile Aberration').first()
        self.assertEquals(
            aberration.basecard.filing_name,
            'insectile aberration')
        self.assertEquals(aberration.basecard.cmc, 0)
        delver = aberration.get_double_faced_card()
        self.assertIsNotNone(delver)
        self.assertEquals(delver.basecard.name, 'Delver of Secrets')
        self.assertEquals(delver.basecard.cmc, 1)
        self.assertEquals(
            delver.basecard.physicalcard.id,
            aberration.basecard.physicalcard.id)

    def test_get_double_faced_card_not(self):
        mss = Card.playables.get_latest_printing().filter(
            basecard__filing_name__exact='monastery swiftspear').first()
        self.assertEquals(mss.basecard.name, 'Monastery Swiftspear')
        foo = mss.get_double_faced_card()
        self.assertIsNone(foo)

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


class ViewsTestCase(TestCase):

    def test_basic_addition(self):
        self.assertEqual(1 + 1, 2)

    def test_cards_paginated_default_sort(self):
        self.assertEqual(1 + 1, 2)
