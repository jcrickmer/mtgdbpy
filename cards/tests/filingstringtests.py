# -*- coding: utf-8 -*-

from django.test import TestCase, TransactionTestCase, RequestFactory
from django_nose import FastFixtureTestCase
from cards.text_utils import filing_string

import json
import sys

err = sys.stderr


class FilingStringTestCase(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        return

    def test_one(self):
        val = 'Simple'
        result = filing_string(val)
        self.assertEquals(result, 'simple')

    def test_two_words(self):
        val = 'Simple words'
        result = filing_string(val)
        self.assertEquals(result, 'simple words')

    def test_three_words(self):
        val = 'Simple English words'
        result = filing_string(val)
        self.assertEquals(result, u'simple english words')

    def test_acute(self):
        val = u'My résumé'
        result = filing_string(val)
        self.assertEquals(result, u'my resume')

    def test_multi_diacritic(self):
        val = u'æther manœuvre Œdipus Æthelthryth naïve'
        result = filing_string(val)
        self.assertEquals(result, u'aether manoeuvre oedipus aethelthryth naive')

    def test_10f_3_digit(self):
        val = u'ď'
        result = filing_string(val)
        self.assertEquals(result, u'd')

    def test_dash_one(self):
        val = u'test of the-Dash'
        result = filing_string(val)
        self.assertEquals(result, u'test of the dash')

    def test_dash_two(self):
        val = u'test of the - Dash'
        result = filing_string(val)
        self.assertEquals(result, u'test of the   dash')

    def test_dash_three(self):
        val = u'Il-vec it'
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_dash_four(self):
        val = u'-Il-vec it'
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_dash_five(self):
        val = u'Il-vec it-'
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_endash_one(self):
        val = u'test of the\u2013Dash'
        result = filing_string(val)
        self.assertEquals(result, u'test of the dash')

    def test_endash_two(self):
        val = u'test of the \u2013 Dash'
        result = filing_string(val)
        self.assertEquals(result, u'test of the   dash')

    def test_endash_three(self):
        val = u'Il\u2013vec it'
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_endash_four(self):
        val = u'\u2013Il\u2013vec it'
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_endash_five(self):
        val = u'Il\u2013vec it\u2013'
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_emdash_one(self):
        val = u'test of the\u2014Dash'
        result = filing_string(val)
        self.assertEquals(result, u'test of the dash')

    def test_emdash_two(self):
        val = u'test of the \u2014 Dash'
        result = filing_string(val)
        self.assertEquals(result, u'test of the   dash')

    def test_emdash_three(self):
        val = u'Il\u2014vec it'
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_emdash_four(self):
        val = u'\u2014Il\u2014vec it'
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_emdash_five(self):
        val = u'Il\u2014vec it\u2014'
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_apos_one(self):
        val = u"test of the'Dash"
        result = filing_string(val)
        self.assertEquals(result, u'test of thedash')

    def test_apos_two(self):
        val = u"test of the ' Dash"
        result = filing_string(val)
        self.assertEquals(result, u'test of the  dash')

    def test_apos_three(self):
        val = u"Il'vec it"
        result = filing_string(val)
        self.assertEquals(result, u'ilvec it')

    def test_apos_four(self):
        val = u"'Il'vec it"
        result = filing_string(val)
        self.assertEquals(result, u'ilvec it')

    def test_apos_five(self):
        val = u"Il'vec it'"
        result = filing_string(val)
        self.assertEquals(result, u'ilvec it')

    def test_period_one(self):
        val = u"test of the.Period"
        result = filing_string(val)
        self.assertEquals(result, u'test of the period')

    def test_period_two(self):
        val = u"test of the . Period"
        result = filing_string(val)
        self.assertEquals(result, u'test of the   period')

    def test_period_three(self):
        val = u"Il.vec it"
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_period_four(self):
        val = u".Il.vec it"
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_period_five(self):
        val = u"Il.vec it."
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_ellipse_one(self):
        val = u"test of the\u2026Ellipse"
        result = filing_string(val)
        self.assertEquals(result, u'test of the ellipse')

    def test_ellipse_two(self):
        val = u"test of the \u2026 Ellipse"
        result = filing_string(val)
        self.assertEquals(result, u'test of the   ellipse')

    def test_ellipse_three(self):
        val = u"Il\u2026vec it"
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_ellipse_four(self):
        val = u"\u2026Il\u2026vec it"
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_ellipse_five(self):
        val = u"Il\u2026vec it\u2026"
        result = filing_string(val)
        self.assertEquals(result, u'il vec it')

    def test_number_zero(self):
        val = u"0"
        result = filing_string(val)
        self.assertEquals(result, u'000000000')

    def test_number_one(self):
        val = u"1"
        result = filing_string(val)
        self.assertEquals(result, u'000000001')

    def test_number_onehundredmillion(self):
        val = u"100000000"
        result = filing_string(val)
        self.assertEquals(result, u'100000000')

    def test_number_onehundredmillioncomma(self):
        val = u"100,000,000"
        result = filing_string(val)
        self.assertEquals(result, u'100000000')

    def test_midnumber_zero(self):
        val = u"hello 0 bye"
        result = filing_string(val)
        self.assertEquals(result, u'hello 000000000 bye')

    def test_midnumber_one(self):
        val = u"hello 1 bye"
        result = filing_string(val)
        self.assertEquals(result, u'hello 000000001 bye')

    def test_midnumber_onehundredmillion(self):
        val = u"hello 100000000 bye"
        result = filing_string(val)
        self.assertEquals(result, u'hello 100000000 bye')

    def test_midnumber_onehundredmillioncomma(self):
        val = u"hello 100,000,000 bye"
        result = filing_string(val)
        self.assertEquals(result, u'hello 100000000 bye')

    def test_midnumber_zerodec(self):
        val = u"hello 0.5 bye"
        result = filing_string(val)
        self.assertEquals(result, u'hello 000000000.5 bye')

    def test_midnumber_onedec(self):
        val = u"hello 1.5 bye"
        result = filing_string(val)
        self.assertEquals(result, u'hello 000000001.5 bye')

    def test_midnumber_onehundredmilliondec(self):
        val = u"hello 100000000.5 bye"
        result = filing_string(val)
        self.assertEquals(result, u'hello 100000000.5 bye')

    def test_midnumber_onehundredmillioncommadec(self):
        val = u"hello 100,000,000.5 bye"
        result = filing_string(val)
        self.assertEquals(result, u'hello 100000000.5 bye')

    def test_number_madness(self):
        val = u"9 people , . s 8 about 4.6757 OYSTERS in .8 seconds 2"
        result = filing_string(val)
        self.assertEquals(result, u'000000009 people    s 000000008 about 000000004.6757 oysters in 000000000.8 seconds 000000002')

    def test_number_madness2(self):
        val = u".9 people , . s 8 about 4.6757 OYSTERS in 7.1 seconds .2"
        result = filing_string(val)
        self.assertEquals(result, u'000000000.9 people    s 000000008 about 000000004.6757 oysters in 000000007.1 seconds 000000000.2')

    def test_punct_1(self):
        val = u"hello ! # $ % ' ( ) * + , - / : ; < > = ? [ ] \\ ^ _ { | } ~ there"
        result = filing_string(val)
        self.assertEquals(result, u'hello                             there')
