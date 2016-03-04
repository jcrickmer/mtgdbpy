from django.test import TestCase, TransactionTestCase
from django_nose import FastFixtureTestCase
from cards.models import Color, Rarity, Type, Subtype, PhysicalCard, Card, BaseCard, CardRating, ExpansionSet, FormatBasecard, SearchPredicate, CardManager, SortDirective
FormatNotSpecifiedException = CardManager.FormatNotSpecifiedException
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction
import sys
err = sys.stderr


# class CardManagerROTestCase(FastFixtureTestCase):
class CardManagerROTestCase(TestCase):
    fixtures = ['mtgdbapp_testdata', ]

    def test_all(self):
        cards = Card.playables.search()
        self.assertEquals(len(list(cards)), 381)

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
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'delver'
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 1)
        for c in cards:
            self.assertEquals(c.basecard.name, 'Delver of Secrets')

    def test_name_c_urzasmine(self):
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'urzas mine'
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 1)

    def test_name_c_urzas(self):
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
        self.assertEquals(len(list(cards)), 381 - 3)

    ''' Rules Text equality '''

    def test_rules_e_flying(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'flying'  # Delver double
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1)

    def test_rules_c_flying(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'flying'
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 34)

    def test_rules_c_foo(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'foobar rainbows'
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_rules_ne_flying(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'flying'
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        # Delver/Insectile throws this off. The correct answer is 381
        self.assertEquals(len(list(cards)), 381 - 0)

    def test_rules_nc_flying(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'flying'
        a.operator = a.CONTAINS
        a.negative = True
        cards = Card.playables.search(a)
        # Delver/Insectile throws this off. The correct answer is 348
        self.assertEquals(len(list(cards)), 381 - 33)

    ''' CMC equality '''

    def test_cmc_e_0(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 105)

    def test_cmc_e_n2(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_e_1(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 70)

    def test_cmc_e_100(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 100
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_ne_0(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 278)

    def test_cmc_ne_n2(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381)

    def test_cmc_ne_1(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 313)

    def test_cmc_ne_100(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 100
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381)

    ''' CMC less than '''

    def test_cmc_lt_0(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_lt_n2(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_lt_1(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 105)

    def test_cmc_lt_100(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 100
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381)

    def test_cmc_nlt_0(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381)

    def test_cmc_nlt_n2(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381)

    def test_cmc_nlt_1(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 278)

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
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 278)

    def test_cmc_gt_n2(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381)

    def test_cmc_gt_1(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 209)

    def test_cmc_gt_100(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 100
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_ngt_0(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 0
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 105)

    def test_cmc_ngt_n2(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = -2
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_cmc_ngt_1(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 1
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 174)

    def test_cmc_ngt_100(self):
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 100
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381)

    ''' Toughness equality '''

    def test_toughness_e_0(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 4)

    def test_toughness_e_n2(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_e_1(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 34)

    def test_toughness_e_100(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_ne_0(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 111)

    def test_toughness_ne_n2(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    def test_toughness_ne_1(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 82)

    def test_toughness_ne_100(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    ''' Toughness less than '''

    def test_toughness_lt_0(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_lt_n2(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_lt_1(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 4)

    def test_toughness_lt_100(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    def test_toughness_nlt_0(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    def test_toughness_nlt_n2(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    def test_toughness_nlt_1(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 111)

    def test_toughness_nlt_100(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    ''' Toughness greater than '''

    def test_toughness_gt_0(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 111)

    def test_toughness_gt_n2(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    def test_toughness_gt_1(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 78)

    def test_toughness_gt_100(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_ngt_0(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 0
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 4)

    def test_toughness_ngt_n2(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = -2
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_toughness_ngt_1(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 1
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 38)

    def test_toughness_ngt_100(self):
        a = SearchPredicate()
        a.term = 'toughness'
        a.value = 100
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    ''' Power equality '''

    def test_power_e_0(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 14)

    def test_power_e_n2(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_e_1(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 25)

    def test_power_e_100(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_ne_0(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 101)

    def test_power_ne_n2(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    def test_power_ne_1(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 91)

    def test_power_ne_100(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    ''' Power less than '''

    def test_power_lt_0(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_lt_n2(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_lt_1(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 14)

    def test_power_lt_100(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    def test_power_nlt_0(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    def test_power_nlt_n2(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    def test_power_nlt_1(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 101)

    def test_power_nlt_100(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    ''' Power greater than '''

    def test_power_gt_0(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 101)

    def test_power_gt_n2(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    def test_power_gt_1(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 77)

    def test_power_gt_100(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_ngt_0(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 0
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 14)

    def test_power_ngt_n2(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = -2
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_power_ngt_1(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 1
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 39)

    def test_power_ngt_100(self):
        a = SearchPredicate()
        a.term = 'power'
        a.value = 100
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    ''' Loyalty equality '''

    def test_loyalty_e_0(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_e_n2(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_e_1(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 1
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_e_100(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 100
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_ne_0(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_loyalty_ne_n2(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_loyalty_ne_1(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 1
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_loyalty_ne_100(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 100
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    ''' Loyalty less than '''

    def test_loyalty_lt_0(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_lt_n2(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_lt_1(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 1
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_lt_100(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 100
        a.operator = a.LESS_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_loyalty_nlt_0(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_loyalty_nlt_n2(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_loyalty_nlt_1(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 1
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_loyalty_nlt_100(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 100
        a.operator = a.LESS_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    ''' Loyalty greater than '''

    def test_loyalty_gt_0(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_loyalty_gt_n2(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_loyalty_gt_1(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 1
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_loyalty_gt_100(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 100
        a.operator = a.GREATER_THAN
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_ngt_0(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 0
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_ngt_n2(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = -2
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_ngt_1(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 1
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_loyalty_ngt_100(self):
        a = SearchPredicate()
        a.term = 'loyalty'
        a.value = 100
        a.operator = a.GREATER_THAN
        a.negative = True
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

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

    def test_rarity_e_u(self):
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'u'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 101)

    def test_rarity_e_z(self):
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'z'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_rarity_e_b(self):
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'b'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_rarity_e_null(self):
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = None
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_rarity_ne_u(self):
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'u'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 300)

    def test_rarity_ne_z(self):
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'z'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381)

    def test_rarity_ne_b(self):
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = 'b'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 375)

    def test_rarity_ne_null(self):
        a = SearchPredicate()
        a.term = 'rarity'
        a.value = None
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381)

    ''' Color equality '''

    def test_color_e_w(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'w'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 63)

    def test_color_e_z(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'z'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_color_e_b(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'b'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 41)

    def test_color_e_c(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'C'
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 134)

    def test_color_e_null(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = None
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_color_ne_u(self):
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
        self.assertEquals(len(list(cards)), 381 - 57)

    def test_color_ne_z(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'z'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381)

    def test_color_ne_b(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'b'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 381 - 41)

    def test_color_ne_c(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'C'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 381 - 134)

    def test_color_ne_null(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = None
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381)

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
        a = SearchPredicate()
        a.term = 'type'
        a.value = 3
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 115)

    def test_type_e_instant(self):
        a = SearchPredicate()
        a.term = 'type'
        a.value = 5
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 74)

    def test_type_e_legendary(self):
        a = SearchPredicate()
        a.term = 'type'
        a.value = 7
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 25)

    def test_type_ne_creature(self):
        a = SearchPredicate()
        a.term = 'type'
        a.value = 3
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381 - 115)

    # REVISIT - need test for enchantment creature

    ''' Subtype equality '''

    def test_subtype_e_warrior(self):
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 269
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 9)

    def test_subtype_e_aura(self):
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 17
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 8)

    def test_subtype_e_artificer(self):
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 13
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 0)

    def test_subtype_e_karn(self):
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 125
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1)

    def test_subtype_ne_warrior(self):
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 269
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 381 - 9)

    def test_subtype_ne_artificer(self):
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 13
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 381 - 0)

    ''' Multiple Fields '''

    def test_name_cmc_1(self):
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
        self.assertEquals(len(list(cards)), 1)

    def test_name_type_multi(self):
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
        self.assertEquals(len(list(cards)), 90)

    def test_type_cmc_0(self):
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
        self.assertEquals(len(list(cards)), 5)

    def test_subtype_cmc_multi(self):
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
        a = SearchPredicate()
        a.term = 'cmc'
        a.value = 3
        a.operator = a.LESS_THAN
        a.negative = False
        b = SortDirective()
        b.term = 'name'
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 255)
        self.assertEquals(cards[0].basecard.name, 'Abrupt Decay')
        self.assertEquals(cards[1].basecard.name, "Ajani's Presence")
        self.assertEquals(cards[254].basecard.name, 'Young Pyromancer')

    def test_sort_name_multi_desc(self):
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
        self.assertEquals(len(list(cards)), 255)
        self.assertEquals(cards[254].basecard.name, 'Abrupt Decay')
        self.assertEquals(cards[253].basecard.name, "Ajani's Presence")
        self.assertEquals(cards[0].basecard.name, 'Young Pyromancer')

    def test_sort_cr_multi(self):
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
        self.assertEquals(len(list(cards)), 255)
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
        self.assertEquals(len(list(cards)), 381 - 41)

    # some random bug tests
    def test_name_g_sql(self):
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
        self.assertEquals(len(list(cards)), 140)

    def test_legendary_creatures(self):
        a = SearchPredicate()
        a.term = 'type'
        a.operator = a.EQUALS
        a.value = 7
        b = SearchPredicate()
        b.term = 'type'
        b.operator = b.EQUALS
        b.value = 3
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 19)
        self.assertEquals(cards[0].basecard.filing_name, 'anafenza the foremost')
        self.assertEquals(cards[1].basecard.filing_name, 'azusa lost but seeking')
        self.assertEquals(cards[18].basecard.filing_name, 'vendilion clique')

    def test_warrior_goblins(self):
        a = SearchPredicate()
        a.term = 'subtype'
        a.operator = a.EQUALS
        a.value = 269
        b = SearchPredicate()
        b.term = 'subtype'
        b.operator = b.EQUALS
        b.value = 94
        cards = Card.playables.search(a, b)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 5)
        self.assertEquals(cards[0].basecard.filing_name, 'akki avalanchers')
        self.assertEquals(cards[1].basecard.filing_name, u'foundry street denizen')
        self.assertEquals(cards[4].basecard.filing_name, 'mogg war marshal')

    def test_white_green(self):
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
        self.assertEquals(len(list(cards)), 11)
        self.assertEquals(cards[0].basecard.filing_name, u'abzan charm')
        self.assertEquals(cards[1].basecard.filing_name, u'anafenza the foremost')
        self.assertEquals(cards[4].basecard.filing_name, u'kitchen finks')

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
        self.assertEquals(len(list(cards)), 381)  # matches all cards, of course

    def test_rules_sql_inject5(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = "doesn't"
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 2)

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
