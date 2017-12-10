# -*- coding: utf-8 -*-

from django.test import TestCase, TransactionTestCase
from django_nose import FastFixtureTestCase
from cards.models import Color, Rarity, Type, Subtype, PhysicalCard, Card, BaseCard, CardRating, ExpansionSet, FormatBasecard, SearchPredicate, CardManager, SortDirective
FormatNotSpecifiedException = CardManager.FormatNotSpecifiedException
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction
from unittest import skip
from nose.plugins.skip import Skip
import sys
err = sys.stderr


PLAYABLE_CARD_COUNT = 1617

# class CardManagerROTestCase(FastFixtureTestCase):


class CardManagerROTestCase(TestCase):
    fixtures = ['mtgdbapp_testdata', ]

    def test_all(self):
        svalidator = '''SELECT count(id) FROM physicalcard WHERE layout NOT IN ('token','plane','scheme','phenomenon','vanguard');'''
        cards = Card.playables.search()
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    def test_name_one_full(self):
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'delver of secrets'
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1)
        for c in cards:
            self.assertEquals(c.basecard.name, 'Delver of Secrets')

    def test_name_one_short_zero(self):
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'delver'
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 0)

    def test_name_one_short_one(self):
        svalidator = '''SELECT pc.id, bc.name, bc.cmc FROM basecard AS bc JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE bc.filing_name LIKE '%delver%' AND pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY physicalcard_id;'''
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'delver'
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 3)
        for c in cards:
            self.assertIn(str('delver'), str(c.basecard.name).lower())

    def test_name_c_urzasmine(self):
        svalidator = '''SELECT pc.id, bc.name, bc.cmc FROM basecard AS bc JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE bc.filing_name LIKE '%urzas mine%' AND pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY physicalcard_id;'''
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'urzas mine'
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 1)

    def test_name_c_urzas(self):
        svalidator = '''SELECT pc.id, bc.name, bc.cmc FROM basecard AS bc JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE bc.filing_name LIKE '%urzas%' AND pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY physicalcard_id;'''
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'urzas'
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 3)

    def test_name_nc_urzas(self):
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'urzas'
        a.operator = a.CONTAINS
        a.negative = True
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT - 3)

    ''' Rules Text equality '''

    def test_rules_e_flying(self):
        svalidator = '''SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE bc.rules_text = 'Flying' AND pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY physicalcard_id;'''
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'flying'  # Delver double
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 6)

    def test_rules_c_flying(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.rules_text LIKE '%flying%' AND
        # pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard')
        # GROUP BY physicalcard_id;
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'flying'
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 247)

    def test_rules_c_foo(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.rules_text LIKE '%foobar rainbows%'
        # AND pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard')
        # GROUP BY physicalcard_id;
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'foobar rainbows'
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_rules_ne_flying(self):
        # NOTE: 'Delver of Secrets' IS included in these results, as it
        # is a card that does not contain 'Flying'. (And it is a card
        # that contains 'Flying'.) This is how Gatherer works, so
        # mimicking its behavior.
        svalidator = '''SELECT pc.id, bc.name FROM physicalcard AS pc JOIN basecard AS bc ON pc.id = bc.physicalcard_id JOIN card AS c ON c.basecard_id = bc.id WHERE  pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard')  AND  bc.rules_text  != 'flying'  GROUP BY pc.id  ORDER BY bc.filing_name ASC;'''
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'flying'
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 1612)

    def test_rules_nc_flying(self):
        # NOTE: 'Delver of Secrets' IS included in these results, as it
        # is a card that does not contain 'Flying'. (And it is a card
        # that contains 'Flying'.) This is how Gatherer works, so
        # mimicking its behavior.
        svalidator = '''SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard') AND bc.rules_text NOT LIKE '%flying%' GROUP BY physicalcard_id;'''
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'flying'
        a.operator = a.CONTAINS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1375)

    ''' CMC equality '''

    def test_cmc_e_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc = 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 146)

    def test_cmc_e_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc = -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_e_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc = 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 180)

    def test_cmc_e_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc = 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 100
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_ne_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc <> 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1471)

    def test_cmc_ne_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc <> -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    def test_cmc_ne_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc <> 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1439)

    def test_cmc_ne_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc <> 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 100
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    ''' CMC less than '''

    def test_cmc_lt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc < 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_lt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc < -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_lt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc < 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 146)

    def test_cmc_lt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc < 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 100
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    def test_cmc_nlt_0(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    def test_cmc_nlt_n2(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    def test_cmc_nlt_1(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT - 146)

    def test_cmc_nlt_100(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 100
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    ''' CMC greater than '''

    def test_cmc_gt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc > 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1471)

    def test_cmc_gt_n2(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    def test_cmc_gt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc > 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1293)

    def test_cmc_gt_100(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 100
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_ngt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc <= 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 146)

    def test_cmc_ngt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc <= -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_ngt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.cmc <= 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 326)

    def test_cmc_ngt_100(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 100
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    ''' Toughness equality '''

    def test_toughness_e_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness = 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 29)

    def test_toughness_e_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness = -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_e_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness = 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 258)

    def test_toughness_e_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness = 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_e_1pstar(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness = '1+*' AND pc.layout NOT
        # IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = '1+*'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 5)

    def test_toughness_e_star(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness = '*' AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = '*'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 10)

    def test_toughness_ne_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness <> 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 968)

    def test_toughness_ne_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness != '-2' AND pc.layout NOT
        # IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    def test_toughness_ne_1(self):
        # SELECT pc.id, bc.name, bc.toughness FROM basecard AS bc JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE bc.toughness != 1 AND pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY physicalcard_id;
        # NOTE: when an integer is given, then we treat ALL toughness as a number. So values with '*' in them are not included.
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 743)

    def test_toughness_ne_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness != '100' AND pc.layout NOT
        # IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    ''' Toughness less than '''

    def test_toughness_lt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness < 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_lt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness < -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_lt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness < 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 29)

    def test_toughness_lt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness < 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    def test_toughness_nlt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness >= 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    def test_toughness_nlt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness >= -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    def test_toughness_nlt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness >= 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 968)

    def test_toughness_nlt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness >= 100 AND pc.layout NOT
        # IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    ''' Toughness greater than '''

    def test_toughness_gt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness > 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 968)

    def test_toughness_gt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness > -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    def test_toughness_gt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness > 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 714)

    def test_toughness_gt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness > 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_ngt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness <= 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 29)

    def test_toughness_ngt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness <= -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_ngt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness <= 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 287)

    def test_toughness_ngt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.toughness <= 100 AND pc.layout NOT
        # IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    ''' Power equality '''

    def test_power_e_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power = 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 73)

    def test_power_e_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power = -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_e_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power = 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 225)

    def test_power_e_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power = 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_ne_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power != 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 924)

    def test_power_ne_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power != -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    def test_power_ne_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power != 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 774)

    def test_power_ne_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power != 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    ''' Power less than '''

    def test_power_lt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power < 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_lt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power < -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_lt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power < 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 73)

    def test_power_lt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power < 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    def test_power_nlt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power >= 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    def test_power_nlt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power >= -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    def test_power_nlt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power >= 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 924)

    def test_power_nlt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power >= 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    ''' Power greater than '''

    def test_power_gt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power > 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 924)

    def test_power_gt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power > -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    def test_power_gt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power > 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 701)

    def test_power_gt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power > 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_ngt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power <= 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 73)

    def test_power_ngt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power <= -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_ngt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power <= 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 298)

    def test_power_ngt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.power <= 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 997)

    ''' Loyalty equality '''

    def test_loyalty_e_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty = 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_e_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty = -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_e_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty = 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 1
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_e_4(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty = 4 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 4
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 20)

    def test_loyalty_e_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty = 4 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 100
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_ne_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty != 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 62)

    def test_loyalty_ne_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty != -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 62)

    def test_loyalty_ne_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty != 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 1
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 62)

    def test_loyalty_ne_4(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty != 4 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 4
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 42)

    ''' Loyalty less than '''

    def test_loyalty_lt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty < 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_lt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty < -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_lt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty < 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 1
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_lt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty < 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 100
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 62)

    def test_loyalty_nlt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty >= 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 62)

    def test_loyalty_nlt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty >= -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 62)

    def test_loyalty_nlt_1(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty >= 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 1
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 62)

    def test_loyalty_nlt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty >= 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 100
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    ''' Loyalty greater than '''

    def test_loyalty_gt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty > 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 62)

    def test_loyalty_gt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty > -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 62)

    def test_loyalty_gt_4(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty > 4 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 4
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 17)

    def test_loyalty_gt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty > 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 100
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_ngt_0(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty <= 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_ngt_n2(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty <= -2 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_ngt_4(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty <= 4 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 4
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 45)

    def test_loyalty_ngt_100(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE bc.loyalty <= 100 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 100
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 62)

    ''' Cardrating equality '''

    def test_cardrating_fnse(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 0
        a.operator = a.EQUALS
        try:
            self.assertRaises(FormatNotSpecifiedException, Card.playables.search(a))
        except FormatNotSpecifiedException:
            self.assertEquals(1, 1)
            pass
        #self.assertRaises(Exception, Card.playables.search(a))

    def test_cardrating_e_0(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 0
        a.operator = a.EQUALS
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 0)

    def test_cardrating_e_n2(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = -2
        a.operator = a.EQUALS
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 0)

    def test_cardrating_e_29(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = round(29.9267473817879 * 20.0, 3)
        a.operator = a.EQUALS
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 1)

    def test_cardrating_e_49(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 49 * 20
        a.operator = a.EQUALS
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 0)

    def test_cardrating_ne_0(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 0
        a.operator = a.EQUALS
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 381)

    def test_cardrating_ne_n2(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = -2
        a.operator = a.EQUALS
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 381)

    def test_cardrating_ne_29(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = round(29.9267473817879 * 20.0, 3)
        a.operator = a.EQUALS
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 380)

    def test_cardrating_ne_100(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 49 * 20
        a.operator = a.EQUALS
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 381)

    ''' Cardrating less than '''

    def test_cardrating_lt_0(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 0
        a.operator = a.LESS_THAN
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 0)

    def test_cardrating_lt_n2(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = -2
        a.operator = a.LESS_THAN
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 0)

    def test_cardrating_lt_29(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = round(29.9267473817879 * 20.0, 3)
        a.operator = a.LESS_THAN
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 165)

    def test_cardrating_lt_100(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 49 * 20
        a.operator = a.LESS_THAN
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 381)

    def test_cardrating_nlt_0(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 0
        a.operator = a.LESS_THAN
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 381)

    def test_cardrating_nlt_n2(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = -2
        a.operator = a.LESS_THAN
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 381)

    def test_cardrating_nlt_29(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = round(29.9267473817879 * 20.0, 3)
        a.operator = a.LESS_THAN
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 216)

    def test_cardrating_nlt_100(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 49 * 20
        a.operator = a.LESS_THAN
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 0)

    ''' Cardrating greater than '''

    def test_cardrating_gt_0(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 0
        a.operator = a.GREATER_THAN
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 381)

    def test_cardrating_gt_n2(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = -2
        a.operator = a.GREATER_THAN
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 381)

    def test_cardrating_gt_29(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = round(29.9267473817879 * 20.0, 3)
        a.operator = a.GREATER_THAN
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 215)

    def test_cardrating_gt_100(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 49 * 20
        a.operator = a.GREATER_THAN
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 0)

    def test_cardrating_ngt_0(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 0
        a.operator = a.GREATER_THAN
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 0)

    def test_cardrating_ngt_n2(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = -2
        a.operator = a.GREATER_THAN
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 0)

    def test_cardrating_ngt_29(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = round(29.9267473817879 * 20.0, 3)
        a.operator = a.GREATER_THAN
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 166)

    def test_cardrating_ngt_100(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = 49 * 20
        a.operator = a.GREATER_THAN
        a.negative = True
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 381)

    ''' Cardrating format out of order '''

    def test_cardrating_ff(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = round(29.9267473817879 * 20.0, 3)
        a.operator = a.GREATER_THAN
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(b, a)
        self.assertEquals(len(list(cards)), 215)

    def test_cardrating_fl(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = round(29.9267473817879 * 20.0, 3)
        a.operator = a.GREATER_THAN
        b = SearchPredicate()
        b.term = 'format'
        b.value = 1
        b.operator = a.EQUALS
        cards = Card.playables.search(a, b)
        self.assertEquals(len(list(cards)), 215)

    ''' Rarity equality '''
    # REVISIT - need to be able to test cards like Rancor and Oblivion Ring, which were printed at different rarities in different sets!

    def test_rarity_e_u(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM card JOIN
        # basecard AS bc ON card.basecard_id = bc.id WHERE card.rarity IN
        # ('u','U') GROUP BY bc.physicalcard_id;
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'u'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 529)

    def test_rarity_e_z(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM card JOIN
        # basecard AS bc ON card.basecard_id = bc.id WHERE card.rarity IN
        # ('Z','z') GROUP BY bc.physicalcard_id;
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'z'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_rarity_e_b(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM card JOIN
        # basecard AS bc ON card.basecard_id = bc.id WHERE card.rarity IN
        # ('b','B') GROUP BY bc.physicalcard_id;
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'b'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 10)

    def test_rarity_e_null(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM card JOIN
        # basecard AS bc ON card.basecard_id = bc.id WHERE card.rarity IS NULL
        # GROUP BY bc.physicalcard_id;
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = None
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    @skip('Needs fix. Not sure why this is failing...')
    def test_rarity_ne_u(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM card JOIN
        # basecard AS bc ON card.basecard_id = bc.id WHERE card.rarity NOT IN
        # ('u','U') GROUP BY bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'u'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1266)

    def test_rarity_ne_z(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM card JOIN
        # basecard AS bc ON card.basecard_id = bc.id WHERE card.rarity NOT IN
        # ('u','U') GROUP BY bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'z'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    @skip('Needs fix. Not sure why this is failing...')
    def test_rarity_ne_b(self):
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'b'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT - 10)  # inverse of test_rarity_e_b

    def test_rarity_ne_null(self):
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = None
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    ''' Color equality '''

    def test_color_e_w(self):
        # SELECT bc.physicalcard_id, bc.name , bc.filing_name FROM cardcolor AS cc
        # JOIN basecard AS bc ON cc.basecard_id = bc.id WHERE cc.color_id IN
        # ('w','W') GROUP BY bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'w'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 388)

    def test_color_e_z(self):
        # SELECT bc.physicalcard_id, bc.name , bc.filing_name FROM cardcolor AS cc
        # JOIN basecard AS bc ON cc.basecard_id = bc.id WHERE cc.color_id IN
        # ('z','Z') GROUP BY bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'z'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_color_e_b(self):
        # SELECT bc.physicalcard_id, bc.name , bc.filing_name FROM cardcolor AS cc
        # JOIN basecard AS bc ON cc.basecard_id = bc.id WHERE cc.color_id IN
        # ('b','B') GROUP BY bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'b'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 268)

    def test_color_e_c(self):
        # SELECT bc.physicalcard_id, bc.name , bc.filing_name FROM cardcolor AS cc
        # JOIN basecard AS bc ON cc.basecard_id = bc.id WHERE cc.color_id IN
        # ('c','C') GROUP BY bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'C'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 108)

    def test_color_e_null(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = None
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_color_ne_u(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE pc.id NOT IN (SELECT bc.physicalcard_id
        # FROM cardcolor AS cc JOIN basecard AS bc ON cc.basecard_id = bc.id WHERE
        # cc.color_id IN ('u','U')) AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'u'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        # NOTE that if you look at all of the blue cards, Insectile Aberation is
        # in that list. But when you reduce it to the physical cards, it elides
        # with Delver of Secrets (as it should). Thus, we are looking at 57 cards,
        # not 58.
        self.assertEquals(len(list(cards)), 1617 - 336)

    def test_color_ne_z(self):
        # SELECT pc.id FROM basecard AS bc JOIN physicalcard AS pc ON
        # bc.physicalcard_id = pc.id WHERE pc.id NOT IN (SELECT bc.physicalcard_id
        # FROM cardcolor AS cc JOIN basecard AS bc ON cc.basecard_id = bc.id WHERE
        # cc.color_id IN ('Z','z')) AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'z'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    def test_color_ne_b(self):
        # SELECT bc.physicalcard_id, bc.name , bc.filing_name FROM cardcolor AS cc
        # JOIN basecard AS bc ON cc.basecard_id = bc.id WHERE bc.physicalcard_id
        # NOT IN (SELECT bc.physicalcard_id FROM cardcolor AS cc JOIN basecard AS
        # bc ON cc.basecard_id = bc.id WHERE color_id IN ('b','B')) GROUP BY
        # bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'b'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT - 268)  # negative of test_color_e_b()

    def test_color_ne_c(self):
        # SELECT bc.physicalcard_id, bc.name , bc.filing_name FROM cardcolor AS cc
        # JOIN basecard AS bc ON cc.basecard_id = bc.id WHERE bc.physicalcard_id
        # NOT IN (SELECT bc.physicalcard_id FROM cardcolor AS cc JOIN basecard AS
        # bc ON cc.basecard_id = bc.id WHERE color_id IN ('c','C')) GROUP BY
        # bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'C'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT - 108)  # negative of test_color_e_c()

    def test_color_ne_null(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = None
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)

    ''' Format equality '''

    def test_format_std(self):
        a = SearchPredicate()
        a.term = 'format'
        a.value = 4
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 136)

    def test_format_edh(self):
        a = SearchPredicate()
        a.term = 'format'
        a.value = 13
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 379)

    def test_format_not_std(self):
        a = SearchPredicate()
        a.term = 'format'
        a.value = 4
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        # NOT CURRENTLY SUPPORTED
        #self.assertEquals(len(list(cards)), 136)

    ''' Type equality '''

    def test_type_e_creature(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM cardtype AS ct
        # JOIN basecard AS bc ON ct.basecard_id = bc.id JOIN physicalcard AS pc ON
        # pc.id = bc.physicalcard_id WHERE ct.type_id = 3 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY pc.id;
        a = SearchPredicate()
        a.term = 'type'
        a.value = 3
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 994)

    def test_type_e_instant(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM cardtype AS ct
        # JOIN basecard AS bc ON ct.basecard_id = bc.id JOIN physicalcard AS pc ON
        # pc.id = bc.physicalcard_id WHERE ct.type_id = 5 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY pc.id;
        a = SearchPredicate()
        a.term = 'type'
        a.value = 5
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 160)

    def test_type_e_legendary(self):
        # SELECT bc.physicalcard_id, bc.name , bc.filing_name FROM cardsupertype
        # AS cst JOIN basecard AS bc ON cst.basecard_id = bc.id JOIN physicalcard
        # AS pc ON pc.id = bc.physicalcard_id WHERE cst.supertype_id = 1 AND
        # pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard')
        # GROUP BY pc.id;
        a = SearchPredicate()
        a.term = 'supertype'
        a.value = 1  # Legendary
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 152)

    def test_type_ne_creature(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM cardtype AS ct
        # JOIN basecard AS bc ON ct.basecard_id = bc.id JOIN physicalcard AS pc ON
        # pc.id = bc.physicalcard_id WHERE bc.physicalcard_id NOT IN (SELECT
        # bc.physicalcard_id FROM cardtype AS ct JOIN basecard AS bc ON
        # ct.basecard_id = bc.id WHERE ct.type_id = 3) AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'type'
        a.value = 3  # Creature
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 623)

    # REVISIT - need test for enchantment creature

    # REVISIT - need tests for supertype

    ''' Is Permanent '''

    def test_ispermanent_true(self):
        # SELECT bc.physicalcard_id FROM basecard AS bc JOIN physicalcard AS pc ON
        # pc.id = bc.physicalcard_id WHERE bc.ispermanent = 1 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY pc.id;
        a = SearchPredicate()
        a.term = 'ispermanent'
        a.value = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1094)

    def test_ispermanent_nottrue(self):
        # SELECT bc.physicalcard_id FROM basecard AS bc JOIN physicalcard AS pc ON
        # pc.id = bc.physicalcard_id WHERE bc.ispermanent != 1 AND pc.layout NOT
        # IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY pc.id;
        a = SearchPredicate()
        a.term = 'ispermanent'
        a.value = True
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 523)

    def test_ispermanent_false(self):
        # SELECT bc.physicalcard_id FROM basecard AS bc JOIN physicalcard AS pc ON
        # pc.id = bc.physicalcard_id WHERE bc.ispermanent = 0 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY pc.id;
        a = SearchPredicate()
        a.term = 'ispermanent'
        a.value = False
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 523)

    def test_ispermanent_notfalse(self):
        # SELECT bc.physicalcard_id FROM basecard AS bc JOIN physicalcard AS pc ON
        # pc.id = bc.physicalcard_id WHERE bc.ispermanent != 0 AND pc.layout NOT
        # IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY pc.id;
        a = SearchPredicate()
        a.term = 'ispermanent'
        a.value = False
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1094)

    ''' Subtype equality '''

    def test_subtype_e_warrior(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM cardsubtype AS
        # cs JOIN basecard AS bc ON cs.basecard_id = bc.id JOIN physicalcard AS pc
        # ON pc.id = bc.physicalcard_id WHERE cs.subtype_id = 269 AND pc.layout
        # NOT IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 269
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 41)

    def test_subtype_e_aura(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM cardsubtype AS
        # cs JOIN basecard AS bc ON cs.basecard_id = bc.id JOIN physicalcard AS pc
        # ON pc.id = bc.physicalcard_id WHERE cs.subtype_id = 17 AND pc.layout NOT
        # IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 17
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 31)

    def test_subtype_e_artificer(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM cardsubtype AS
        # cs JOIN basecard AS bc ON cs.basecard_id = bc.id JOIN physicalcard AS pc
        # ON pc.id = bc.physicalcard_id WHERE cs.subtype_id = 13 AND pc.layout NOT
        # IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 13
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_subtype_e_karn(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM cardsubtype AS
        # cs JOIN basecard AS bc ON cs.basecard_id = bc.id JOIN physicalcard AS pc
        # ON pc.id = bc.physicalcard_id WHERE cs.subtype_id = 125 AND pc.layout
        # NOT IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 125
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1)

    def test_subtype_ne_warrior(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM basecard AS bc
        # JOIN physicalcard AS pc ON pc.id = bc.physicalcard_id WHERE pc.id NOT IN
        # (SELECT bc.physicalcard_id FROM cardsubtype AS cs JOIN basecard AS bc ON
        # cs.basecard_id = bc.id WHERE cs.subtype_id = 269) AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 269
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT - 41)  # inverse of test_subtype_e_warrior

    def test_subtype_ne_artificer(self):
        # SELECT bc.physicalcard_id, bc.name, bc.filing_name FROM basecard AS bc
        # JOIN physicalcard AS pc ON pc.id = bc.physicalcard_id WHERE pc.id NOT IN
        # (SELECT bc.physicalcard_id FROM cardsubtype AS cs JOIN basecard AS bc ON
        # cs.basecard_id = bc.id WHERE cs.subtype_id = 13) AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 13
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT - 9)  # inverse of test_subtype_e_artificer

    ''' Multiple Fields '''

    def test_name_cmc_1(self):
        # SELECT pc.id, bc.filing_name, bc.cmc FROM basecard AS bc JOIN
        # physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE bc.cmc = 6 AND
        # bc.filing_name LIKE '%el%' AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'el'
        a.operator = a.CONTAINS
        a.negative = False
        b = SearchPredicate()
        b.term = 'cmc'
        b.value = 6
        b.operator = a.EQUALS
        b.negative = False
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 13)

    def test_name_type_multi(self):
        # Urza lands
        # SELECT pc.id, bc.name, bc.cmc FROM basecard AS bc JOIN physicalcard AS
        # pc ON bc.physicalcard_id = pc.id WHERE bc.filing_name LIKE '%urz%' AND
        # bc.physicalcard_id IN (SELECT bc.physicalcard_id FROM cardtype AS ct
        # JOIN basecard AS bc ON ct.basecard_id = bc.id WHERE ct.type_id = 6) AND
        # pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard')
        # GROUP BY physicalcard_id;
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'urz'
        a.operator = a.CONTAINS
        a.negative = False
        b = SearchPredicate()
        b.term = 'type'
        b.value = 6
        b.operator = a.EQUALS
        b.negative = False
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 3)

    def test_ne_name_type_multi(self):
        # NOT Urza lands
        # SELECT pc.id, bc.name, bc.cmc FROM basecard AS bc JOIN physicalcard AS
        # pc ON bc.physicalcard_id = pc.id WHERE bc.filing_name NOT LIKE '%urz%'
        # AND bc.physicalcard_id IN (SELECT bc.physicalcard_id FROM cardtype AS ct
        # JOIN basecard AS bc ON ct.basecard_id = bc.id WHERE ct.type_id = 6) AND
        # pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard')
        # GROUP BY physicalcard_id;
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'urz'
        a.operator = a.CONTAINS
        a.negative = True
        b = SearchPredicate()
        b.term = 'type'
        b.value = 6
        b.operator = a.EQUALS
        b.negative = False
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 126)

    def test_type_cmc_0(self):
        # SELECT pc.id, bc.name, bc.cmc FROM basecard AS bc JOIN physicalcard AS
        # pc ON bc.physicalcard_id = pc.id WHERE bc.rules_text LIKE
        # '%strangelove%' AND bc.physicalcard_id IN (SELECT bc.physicalcard_id
        # FROM cardtype AS ct JOIN basecard AS bc ON ct.basecard_id = bc.id WHERE
        # ct.type_id = 3) AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'strangelove'
        a.operator = a.CONTAINS
        a.negative = False
        b = SearchPredicate()
        b.term = 'type'
        b.value = 3
        b.operator = a.EQUALS
        b.negative = False
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 0)

    def test_subtype_cmc_multi(self):
        # SELECT pc.id, bc.name, bc.cmc FROM basecard AS bc JOIN physicalcard AS
        # pc ON bc.physicalcard_id = pc.id WHERE bc.cmc < 2 AND bc.physicalcard_id
        # IN (SELECT bc.physicalcard_id FROM cardsubtype AS cs JOIN basecard AS bc
        # ON cs.basecard_id = bc.id WHERE cs.subtype_id = 109) AND pc.layout NOT
        # IN ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 2
        a.operator = a.LESS_THAN
        a.negative = False
        b = SearchPredicate()
        b.term = 'subtype'
        b.value = 109
        b.operator = a.EQUALS
        b.negative = False
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 19)

    def test_subtype_cmc_multi(self):
        # SELECT pc.id, bc.name, bc.cmc FROM basecard AS bc JOIN physicalcard AS
        # pc ON bc.physicalcard_id = pc.id WHERE bc.cmc < 2 AND bc.physicalcard_id
        # IN (SELECT bc.physicalcard_id FROM cardsubtype AS cs JOIN basecard AS bc
        # ON cs.basecard_id = bc.id WHERE cs.subtype_id = 109) AND
        # bc.physicalcard_id IN (SELECT bc.physicalcard_id FROM formatbasecard AS
        # fbc JOIN basecard AS bc ON fbc.basecard_id = bc.id WHERE fbc.format_id =
        # 4) AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 2
        a.operator = a.LESS_THAN
        a.negative = False
        b = SearchPredicate()
        b.term = 'subtype'
        b.value = 109
        b.operator = a.EQUALS
        b.negative = False
        c = SearchPredicate()
        c.term = 'format'
        c.value = 4
        c.operator = a.EQUALS
        cards = Card.playables.search(a, b, c)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 2)

    ''' Sort '''

    def test_sort_name_multi(self):
        # SELECT pc.id, bc.name, bc.cmc FROM basecard AS bc JOIN physicalcard AS
        # pc ON bc.physicalcard_id = pc.id WHERE bc.cmc < 3 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 3
        a.operator = a.LESS_THAN
        a.negative = False
        b = SortDirective()
        b.term = 'name'
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 618)
        self.assertEquals(cards[0].basecard.name, 'Abandon Hope')
        self.assertEquals(cards[1].basecard.name, "Abrupt Decay")
        self.assertEquals(cards[254].basecard.name, 'Gruul Turf')

    def test_sort_name_multi_desc(self):
        # SELECT pc.id, bc.name, bc.cmc FROM basecard AS bc JOIN physicalcard AS
        # pc ON bc.physicalcard_id = pc.id WHERE bc.cmc < 3 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id ORDER BY bc.filing_name DESC;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 3
        a.operator = a.LESS_THAN
        a.negative = False
        b = SortDirective()
        b.term = 'name'
        b.direction = b.DESC
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 618)
        self.assertEquals(cards[616].basecard.name, 'Abrupt Decay')
        self.assertEquals(cards[4].basecard.name, "Young Pyromancer")
        self.assertEquals(cards[0].basecard.name, '_____')

    def test_sort_cr_multi(self):
        # SELECT pc.id, bc.name, cr.mu FROM basecard AS bc JOIN physicalcard AS pc
        # ON bc.physicalcard_id = pc.id LEFT JOIN cardrating AS cr ON
        # cr.physicalcard_id = pc.id AND cr.format_id = 4 WHERE bc.cmc < 3 AND
        # pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard')
        # GROUP BY pc.id ORDER BY cr.mu DESC;
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 3
        a.operator = a.LESS_THAN
        a.negative = False
        b = SortDirective()
        b.term = 'cardrating'
        b.direction = b.DESC
        b.crs_format_id = 4
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 618)
        self.assertEquals(cards[0].basecard.name, 'Shivan Reef')
        self.assertEquals(cards[1].basecard.name, 'Urborg, Tomb of Yawgmoth')

    def test_sort_color_ne_b(self):
        # see test_color_ne_b - count result should be the same!
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'b'
        a.negative = True
        a.operator = a.EQUALS
        b = SortDirective()
        b.term = 'cardrating'
        b.crs_format_id = 4
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT - 268)  # negative of test_color_e_b()

    # some random bug tests
    def test_name_g_sql(self):
        # SELECT pc.id, bc.name, bc.cmc FROM basecard AS bc JOIN physicalcard AS
        # pc ON bc.physicalcard_id = pc.id WHERE bc.filing_name LIKE '%g%' AND
        # pc.layout NOT IN ('token','plane','scheme','phenomenon','vanguard')
        # GROUP BY physicalcard_id;
        a = SearchPredicate()
        a.term = 'name'
        a.operator = a.CONTAINS
        a.value = 'g'
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        # I am not sure that this is the right answer or not. It returns Ravager
        # of the Fells, which matches. But Huntmaster of the Fells is the front of
        # the card. Is this right? I think that I need users to play with it and
        # offer feedback.
        self.assertEquals(len(list(cards)), 630)

    def test_legendary_creatures(self):
        # SELECT bc.physicalcard_id, bc.filing_name FROM basecard AS bc JOIN
        # physicalcard AS pc ON pc.id = bc.physicalcard_id JOIN cardtype AS ct ON
        # ct.basecard_id = bc.id JOIN cardsupertype AS cst ON cst.basecard_id =
        # bc.id WHERE cst.supertype_id = 1 AND ct.type_id = 3 AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY pc.id ORDER
        # BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'type'
        a.operator = a.EQUALS
        a.value = 3
        b = SearchPredicate()
        b.term = 'supertype'
        b.operator = b.EQUALS
        b.value = 1
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 80)
        self.assertEquals(cards[0].basecard.filing_name, 'akiri line slinger')
        self.assertEquals(cards[1].basecard.filing_name, 'alexi zephyr mage')
        self.assertEquals(cards[78].basecard.filing_name, 'wort the raidmother')

    def test_warrior_goblins(self):
        # SELECT bc.physicalcard_id, bc.name , bc.filing_name FROM cardsubtype AS
        # cs JOIN basecard AS bc ON cs.basecard_id = bc.id WHERE cs.subtype_id =
        # 269 AND bc.physicalcard_id IN (SELECT bc.physicalcard_id FROM
        # cardsubtype AS cs JOIN basecard AS bc ON cs.basecard_id = bc.id WHERE
        # cs.subtype_id = 94) GROUP BY bc.physicalcard_id ORDER BY bc.filing_name;
        a = SearchPredicate()
        a.term = 'subtype'
        a.operator = a.EQUALS
        a.value = 269  # Goblin
        b = SearchPredicate()
        b.term = 'subtype'
        b.operator = b.EQUALS
        b.value = 94  # Warrior
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 8)
        self.assertEquals(cards[0].basecard.filing_name, u'akki avalanchers')
        self.assertEquals(cards[2].basecard.filing_name, u'foundry street denizen')
        self.assertEquals(cards[7].basecard.filing_name, 'mogg war marshal')

    @skip('Needs fix')
    def test_white_green(self):
        # REVISIT!!!
        # SELECT bc.physicalcard_id, bc.name , bc.filing_name FROM cardcolor AS cc
        # JOIN basecard AS bc ON cc.basecard_id = bc.id WHERE cc.color_id IN
        # ('G','g') AND bc.physicalcard_id IN (SELECT bc.physicalcard_id FROM
        # cardcolor AS cc JOIN basecard AS bc ON cc.basecard_id = bc.id WHERE
        # color_id IN ('W','w')) GROUP BY bc.physicalcard_id ORDER BY
        # bc.filing_name;
        a = SearchPredicate()
        a.term = 'color'
        a.operator = a.EQUALS
        a.value = 'w'
        b = SearchPredicate()
        b.term = 'color'
        b.operator = b.EQUALS
        b.value = 'g'
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 34)
        self.assertEquals(cards[0].basecard.filing_name, u'abzan charm')
        self.assertEquals(cards[1].basecard.filing_name, u'ajani mentor of heroes')
        self.assertEquals(cards[4].basecard.physicalcard.get_card_name(), u'Alive/Well')
        self.assertEquals(cards[31].basecard.physicalcard.get_card_name(), u'Tamiyo, Field Researcher')

    def test_white_green_legendary_creatures(self):
        a = SearchPredicate()
        a.term = 'color'
        a.operator = a.EQUALS
        a.value = 'w'
        b = SearchPredicate()
        b.term = 'color'
        b.operator = b.EQUALS
        b.value = 'g'
        c = SearchPredicate()
        c.term = 'type'
        c.operator = c.EQUALS
        c.value = 7
        d = SearchPredicate()
        d.term = 'type'
        d.operator = d.EQUALS
        d.value = 3
        cards = Card.playables.search(a, d, c, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 2)
        self.assertEquals(cards[0].basecard.filing_name, u'anafenza the foremost')
        self.assertEquals(cards[1].basecard.filing_name, 'sigarda host of herons')

    def test_white_green_legendary_creatures_not_black(self):
        e = SearchPredicate()
        e.term = 'color'
        e.operator = e.EQUALS
        e.negative = True
        e.value = 'b'
        a = SearchPredicate()
        a.term = 'color'
        a.operator = a.EQUALS
        a.value = 'w'
        b = SearchPredicate()
        b.term = 'color'
        b.operator = b.EQUALS
        b.value = 'g'
        c = SearchPredicate()
        c.term = 'type'
        c.operator = c.EQUALS
        c.value = 7
        d = SearchPredicate()
        d.term = 'type'
        d.operator = d.EQUALS
        d.value = 3
        cards = Card.playables.search(e, a, d, c, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 1)
        self.assertEquals(cards[0].basecard.filing_name, 'sigarda host of herons')

    def test_white_green_legendary_creatures_not_red(self):
        e = SearchPredicate()
        e.term = 'color'
        e.operator = e.EQUALS
        e.negative = True
        e.value = 'r'
        a = SearchPredicate()
        a.term = 'color'
        a.operator = a.EQUALS
        a.value = 'w'
        b = SearchPredicate()
        b.term = 'color'
        b.operator = b.EQUALS
        b.value = 'g'
        c = SearchPredicate()
        c.term = 'type'
        c.operator = c.EQUALS
        c.value = 7
        d = SearchPredicate()
        d.term = 'type'
        d.operator = d.EQUALS
        d.value = 3
        cards = Card.playables.search(e, a, d, c, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 2)
        self.assertEquals(cards[0].basecard.filing_name, u'anafenza the foremost')
        self.assertEquals(cards[1].basecard.filing_name, 'sigarda host of herons')

    def test_rules_sql_inject1(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = "fo'foo"
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_rules_sql_inject2(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = "';;DROP DB mtgdbpy_test;"
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_rules_sql_inject3(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = "%%%%%%"
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_rules_sql_inject4(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = "%%%%%%"
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), PLAYABLE_CARD_COUNT)  # matches all cards, of course

    def test_rules_sql_inject5(self):
        # SELECT pc.id, bc.name, bc.rules_text FROM basecard AS bc JOIN
        # physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE bc.rules_text
        # LIKE '%doesn''t%' AND pc.layout NOT IN
        # ('token','plane','scheme','phenomenon','vanguard') GROUP BY
        # physicalcard_id;
        a = SearchPredicate()
        a.term = 'rules'
        a.value = "doesn't"
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 28)

    def test_not_color_not_consequential_pre(self):
        # abzan planeswalker
        e = SearchPredicate()
        e.term = 'color'
        e.operator = e.EQUALS
        e.value = 'w'
        a = SearchPredicate()
        a.term = 'color'
        a.operator = a.EQUALS
        a.value = 'g'
        b = SearchPredicate()
        b.term = 'color'
        b.operator = b.EQUALS
        b.value = 'b'
        c = SearchPredicate()
        c.term = 'type'
        c.operator = c.EQUALS
        c.value = 11
        f = SearchPredicate()
        f.term = 'color'
        f.operator = f.EQUALS
        f.value = 'r'
        g = SearchPredicate()
        g.term = 'color'
        g.operator = g.EQUALS
        g.value = 'u'
        cards = Card.playables.search(f, g, e, a, c, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 0)
        #self.assertEquals(cards[0].basecard.filing_name, u'anafenza the foremost')

    def test_not_color_not_consequential(self):
        # abzan planeswalker
        e = SearchPredicate()
        e.term = 'color'
        e.operator = e.EQUALS
        e.value = 'w'
        a = SearchPredicate()
        a.term = 'color'
        a.operator = a.EQUALS
        a.value = 'g'
        b = SearchPredicate()
        b.term = 'color'
        b.operator = b.EQUALS
        b.value = 'b'
        c = SearchPredicate()
        c.term = 'type'
        c.operator = c.EQUALS
        c.value = 11
        f = SearchPredicate()
        f.term = 'color'
        f.operator = f.EQUALS
        f.negative = True
        f.value = 'r'
        g = SearchPredicate()
        g.term = 'color'
        g.operator = g.EQUALS
        g.negative = True
        g.value = 'u'
        cards = Card.playables.search(f, g, e, a, c, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 0)
        #self.assertEquals(cards[0].basecard.filing_name, u'anafenza the foremost')
