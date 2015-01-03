from django.test import TestCase, TransactionTestCase
from django_nose import FastFixtureTestCase
from mtgdbapp.models import Color, Rarity, Type, Subtype, PhysicalCard, Card, BaseCard, CardRating, ExpansionSet, FormatBasecard, SearchPredicate
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction
import sys; err = sys.stderr

class CardManagerROTestCase(FastFixtureTestCase):
    fixtures = ['mtgdbapp_testdata', ]
    def test_all(self):
        cards = Card.playables.search()
        self.assertEquals(len(list(cards)), 381)

    def test_one_full(self):
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'delver of secrets'
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 1)
        for c in cards:
            self.assertEquals(c.basecard.name, 'Delver of Secrets')

    def test_one_short_zero(self):
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'delver'
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 0)

    def test_one_short_one(self):
        a = SearchPredicate()
        a.term = 'name'
        a.value = 'delver'
        a.operator = a.CONTAINS
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 1)
        for c in cards:
            self.assertEquals(c.basecard.name, 'Delver of Secrets')


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
        a.value = round(29.9267473817879 * 20.0,3)
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
        a.value = round(29.9267473817879 * 20.0,3)
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
        a.value = round(29.9267473817879 * 20.0,3)
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
        a.value = round(29.9267473817879 * 20.0,3)
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
        a.value = round(29.9267473817879 * 20.0,3)
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
        a.value = round(29.9267473817879 * 20.0,3)
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


