from django.test import TestCase, TransactionTestCase
from django_nose import FastFixtureTestCase
from mtgdbapp.models import Color, Rarity, Type, Subtype, PhysicalCard, Card, BaseCard, CardRating, ExpansionSet, FormatBasecard, SearchPredicate, CardManager
FormatNotSpecifiedException = CardManager.FormatNotSpecifiedException
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction
import sys; err = sys.stderr

class CardManagerROTestCase(FastFixtureTestCase):
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
        self.assertEquals(len(list(cards)), 381-3)

    ''' Rules Text equality '''

    def test_rules_e_flying(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'flying' # Delver double
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
        self.assertEquals(len(list(cards)), 381-0)

    def test_rules_nc_flying(self):
        a = SearchPredicate()
        a.term = 'rules'
        a.value = 'flying'
        a.operator = a.CONTAINS
        a.negative = True
        cards = Card.playables.search(a)
        # Delver/Insectile throws this off. The correct answer is 348
        self.assertEquals(len(list(cards)), 381-33)



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

    ''' Cardrating format out of order '''
        
    def test_cardrating_ff(self):
        a = SearchPredicate()
        a.term = 'cardrating'
        a.value = round(29.9267473817879 * 20.0,3)
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
        a.value = round(29.9267473817879 * 20.0,3)
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
        a.value = 'c'
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
        # NOTE that if you look at all of the blue cards, Insectile Aberation is in that list. But when you reduce it to the physical cards, it elides with Delver of Secrets (as it should). Thus, we are looking at 57 cards, not 58.
        self.assertEquals(len(list(cards)), 381-57)

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
        self.assertEquals(len(list(cards)), 381-41)

    def test_color_ne_c(self):
        a = SearchPredicate()
        a.term = 'color'
        a.value = 'c'
        a.negative = True
        a.operator = a.EQUALS
        cards = Card.playables.search(a)
        self.assertEquals(len(list(cards)), 381-134)

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
        ## NOT CURRENTLY SUPPORTED
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
        self.assertEquals(len(list(cards)), 381-115)

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
        self.assertEquals(len(list(cards)), 381-9)

    def test_subtype_ne_artificer(self):
        a = SearchPredicate()
        a.term = 'subtype'
        a.value = 13
        a.operator = a.EQUALS
        a.negative = True
        cards = Card.playables.search(a)
        #err.write(str(cards.query) + "\n")
        self.assertEquals(len(list(cards)), 381-0)

