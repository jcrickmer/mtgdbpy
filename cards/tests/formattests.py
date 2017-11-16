# -*- coding: utf-8 -*-

from django.test import TestCase, TransactionTestCase, RequestFactory
from django_nose import FastFixtureTestCase
from cards.models import Color, Rarity, Type, Subtype, PhysicalCard, Card, BaseCard, CardRating, ExpansionSet, FormatBasecard, SearchPredicate, CardManager, SortDirective
from cards.models import Format, FormatBannedCard, FormatExpansionSet
FormatNotSpecifiedException = CardManager.FormatNotSpecifiedException
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction
import json
from datetime import datetime, date
from cards.views import autocomplete
from cards.tests.helper import TestLoadHelper
from cards.management.commands.loadcardjson import Command
import sys
err = sys.stderr


# class CardManagerROTestCase(FastFixtureTestCase):
class FormatTestCase(TestCase):
    #fixtures = ['mtgdbdev_testdata', ]
    black_lotus_json = '''{"layout":"normal",
"type":"Artifact",
"types":["Artifact"],
"multiverseid":3,
"name":"Black Lotus",
"originalType":"Mono Artifact",
"cmc":0,
"rarity":"Rare",
"artist":"Christopher Rush",
"manaCost":"{0}",
"text":"{T}, Sacrifice Black Lotus: Add three mana of any one color to your mana pool.",
"originalText":"Adds 3 mana of any single color of your choice to your mana pool, then is discarded. Tapping this artifact can be played as an interrupt.",
"imageName":"black lotus"
}
'''
    plains_json = '''{"layout":"normal",
"name":"Plains",
"type":"Land","supertypes":["Basic"],"types":["Land"],"originalType":"Basic Land",
"multiverseid":101,
"rarity":"Common",
"artist":"Jason Crickmer",
"text":"","originalText":"",
"number":"1",
"imageName":"plains"
}'''
    island_json = '''{"layout":"normal",
"name":"Island",
"type":"Land","supertypes":["Basic"],"types":["Land"],"originalType":"Basic Land",
"multiverseid":102,
"rarity":"Common",
"artist":"Jason Crickmer",
"text":"","originalText":"",
"number":"2",
"imageName":"island"
}'''
    swamp_json = '''{"layout":"normal",
"name":"Swamp",
"type":"Land","supertypes":["Basic"],"types":["Land"],"originalType":"Basic Land",
"multiverseid":103,
"rarity":"Common",
"artist":"Jason Crickmer",
"text":"","originalText":"",
"number":"3",
"imageName":"swamp"
}'''
    mountain_json = '''{"layout":"normal",
"name":"Mountain",
"type":"Land","supertypes":["Basic"],"types":["Land"],"originalType":"Basic Land",
"multiverseid":104,
"rarity":"Common",
"artist":"Jason Crickmer",
"text":"","originalText":"",
"number":"4",
"imageName":"mountain"
}'''
    forest_json = '''{"layout":"normal",
"name":"Forest",
"type":"Land","supertypes":["Basic"],"types":["Land"],"originalType":"Basic Land",
"multiverseid":105,
"rarity":"Common",
"artist":"Jason Crickmer",
"text":"","originalText":"",
"number":"5",
"imageName":"forest"
}'''
    cavern_of_souls_json = '''{"layout":"normal",
"type":"Land",
"types":["Land"],
"multiverseid":278058,
"name":"Cavern of Souls",
"originalType":"Land",
"rarity":"Rare",
"artist":"Cliff Childs",
"text":"As Cavern of Souls enters the battlefield, choose a creature type.\\n{T}: Add {1} to your mana pool.\\n{T}: Add one mana of any color to your mana pool. Spend this mana only to cast a creature spell of the chosen type, and that spell can't be countered.",
"originalText":"As Cavern of Souls enters the battlefield, choose a creature type.\\n{T}: Add {1} to your mana pool.\\n{T}: Add one mana of any color to your mana pool. Spend this mana only to cast a creature spell of the chosen type, and that spell can't be countered.",
"number":"226",
"imageName":"cavern of souls"
}'''

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def load_card(self, json, name, loadhelper=True, set_abbr='BAR'):
        helper = TestLoadHelper()
        if loadhelper:
            helper.color_loader()
            helper.expansionset_example_loader()
        expset = ExpansionSet.objects.filter(abbr=set_abbr).first()
        tool = Command()
        tool.handle_card_json(json, expset)
        card = BaseCard.objects.filter(name=name).first()
        return card

    def test_format_add_one(self):
        ff = Format.objects.create()
        ff.formatname = 'Standard'
        ff.format = 'Test'
        ff.abbr = 'STD'
        ff.start_date = date(year=2015, month=3, day=5)
        ff.end_date = date(year=2015, month=6, day=30)

        ff.save()

        fdb = Format.objects.filter(abbr='STD').first()

        self.assertEquals(ff.format, 'Test')
        self.assertEquals(fdb.format, 'Test')

        self.assertEquals(ff.formatname, 'Standard')
        self.assertEquals(fdb.formatname, 'Standard')

        self.assertEquals(ff.abbr, 'STD')
        self.assertEquals(fdb.abbr, 'STD')

        self.assertEquals(ff.min_cards_main, 60)
        self.assertEquals(fdb.min_cards_main, 60)

        self.assertEquals(ff.min_cards_side, 0)
        self.assertEquals(fdb.min_cards_side, 0)

        self.assertEquals(ff.max_cards_side, 15)
        self.assertEquals(fdb.max_cards_side, 15)

        self.assertEquals(ff.max_nonbl_card_count, 4)
        self.assertEquals(fdb.max_nonbl_card_count, 4)

        self.assertFalse(ff.uses_command_zone)
        self.assertFalse(fdb.uses_command_zone)

        self.assertIsNone(ff.validator)
        self.assertIsNone(fdb.validator)

        self.assertEquals(ff.start_date, date(year=2015, month=3, day=5))
        self.assertEquals(fdb.start_date, date(year=2015, month=3, day=5))

        self.assertEquals(ff.end_date, date(year=2015, month=6, day=30))
        self.assertEquals(fdb.end_date, date(year=2015, month=6, day=30))

    def test_format_add_uniqname(self):
        ff = Format.objects.create()
        ff.format = 'TestUnique'
        ff.formatname = 'Standard'
        ff.abbr = 'STD'
        ff.start_date = date(year=2015, month=3, day=5)
        ff.end_date = date(year=2015, month=6, day=30)

        ff.save()

        ff2 = Format.objects.create()
        ff2.format = 'TestUnique'
        ff2.formatname = 'Standard'
        ff2.abbr = 'STD'
        ff2.start_date = date(year=2015, month=3, day=5)
        ff2.end_date = date(year=2015, month=6, day=30)

        with self.assertRaises(IntegrityError) as ie:
            ff2.save()

    ''' #sigh, the ORM can't do the type of validation I was hoping for. And I guess that that makes sense. Will need to figure out how to do it in ModelForm in the Admin.
    def test_format_add_overlapping_dates_early(self):
        ff = Format.objects.create()
        ff.format = 'aTest'
        ff.formatname = 'Standard'
        ff.abbr = 'STD'
        ff.start_date = date(year=2015, month=3, day=5)
        ff.end_date = date(year=2015, month=6, day=30)

        ff.save()

        ff2 = Format.objects.create()
        ff2.format = 'aTest2'
        ff2.formatname = 'Standard'
        ff2.abbr = 'STD'
        ff2.start_date = date(year=2015, month=2, day=5)
        ff2.end_date = date(year=2015, month=3, day=31)

        with self.assertRaises(ValidationError) as ie:
            ff2.save()


    def test_format_add_overlapping_dates_late(self):
        ff = Format.objects.create()
        ff.format = 'bTest'
        ff.formatname = 'Standard'
        ff.abbr = 'STD'
        ff.start_date = date(year=2015, month=3, day=5)
        ff.end_date = date(year=2015, month=6, day=30)

        ff.save()

        ff2 = Format.objects.create()
        ff2.format = 'bTest2'
        ff2.formatname = 'Standard'
        ff2.abbr = 'STD'
        ff2.start_date = date(year=2015, month=5, day=5)
        ff2.end_date = date(year=2015, month=7, day=31)

        with self.assertRaises(ValidationError) as ie:
            ff2.save()


    def test_format_add_overlapping_dates_incl(self):
        ff = Format.objects.create()
        ff.format = 'cTest'
        ff.formatname = 'Standard'
        ff.abbr = 'STD'
        ff.start_date = date(year=2015, month=3, day=5)
        ff.end_date = date(year=2015, month=6, day=30)

        ff.save()

        ff2 = Format.objects.create()
        ff2.format = 'cTest2'
        ff2.formatname = 'Standard'
        ff2.abbr = 'STD'
        ff2.start_date = date(year=2015, month=4, day=5)
        ff2.end_date = date(year=2015, month=5, day=31)

        with self.assertRaises(ValidationError) as ie:
            ff2.save()


    def test_format_add_overlapping_dates_excl(self):
        ff = Format.objects.create()
        ff.format = 'dTest'
        ff.formatname = 'Standard'
        ff.abbr = 'STD'
        ff.start_date = date(year=2015, month=3, day=5)
        ff.end_date = date(year=2015, month=6, day=30)

        ff.save()

        ff2 = Format.objects.create()
        ff2.format = 'dTest2'
        ff2.formatname = 'Standard'
        ff2.abbr = 'STD'
        ff2.start_date = date(year=2015, month=2, day=1)
        ff2.end_date = date(year=2015, month=8, day=31)

        with self.assertRaises(ValidationError) as ie:
            ff2.save()
'''

    def test_format_add_expset(self):
        ff = Format.objects.create()
        ff.format = 'tfae1Test'
        ff.formatname = 'Standard'
        ff.abbr = 'STD'
        ff.start_date = date(year=2017, month=7, day=1)
        ff.end_date = date(year=2017, month=10, day=31)

        ff.save()

        expset = ExpansionSet.objects.create()
        expset.name = 'Andalve'
        expset.abbr = 'AND'
        expset.save()

        fes = FormatExpansionSet.objects.create(format=ff, expansionset=expset)
        fes.save()

        self.assertEquals(len(ff.formatexpansionset_set.all()), 1)

    def test_format_add_expset_proc_empty(self):
        ff = Format.objects.create()
        ff.format = 'tfae1Test'
        ff.formatname = 'Standard'
        ff.abbr = 'STD'
        ff.start_date = date(year=2017, month=7, day=1)
        ff.end_date = date(year=2017, month=10, day=31)

        ff.save()

        expset = ExpansionSet.objects.create()
        expset.name = 'Andalve'
        expset.abbr = 'AND'
        expset.save()

        fes = FormatExpansionSet.objects.create(format=ff, expansionset=expset)
        fes.save()

        self.assertEquals(len(ff.formatexpansionset_set.all()), 1)

        self.assertEquals(len(ff.formatbasecard_set.all()), 0)

        ff.populate_format_cards()

        self.assertEquals(len(ff.formatbasecard_set.all()), 0)

    def test_format_add_expset_proc_empty_withbc(self):
        ff = Format.objects.create()
        ff.format = 'tfae1wbcTest'
        ff.formatname = 'Standard'
        ff.abbr = 'STD'
        ff.start_date = date(year=2017, month=7, day=1)
        ff.end_date = date(year=2017, month=10, day=31)

        ff.save()

        expset = ExpansionSet.objects.create()
        expset.name = 'Andalve2'
        expset.abbr = 'AND2'
        expset.save()

        fes = FormatExpansionSet.objects.create(format=ff, expansionset=expset)
        fes.save()

        bcard = self.load_card(self.cavern_of_souls_json, 'Cavern of Souls')
        fbc = FormatBannedCard.objects.create(format=ff, physicalcard=bcard.physicalcard)
        fbc.save()

        self.assertEquals(len(ff.formatexpansionset_set.all()), 1)

        self.assertEquals(len(ff.formatbasecard_set.all()), 0)

        ff.populate_format_cards()

        self.assertEquals(len(ff.formatbasecard_set.all()), 0)

    def test_format_add_expset_proc(self):
        ff = Format.objects.create()
        ff.format = 'tfae2Test'
        ff.formatname = 'Standard'
        ff.abbr = 'STD'
        ff.start_date = date(year=2017, month=7, day=1)
        ff.end_date = date(year=2017, month=10, day=31)

        ff.save()

        expset = ExpansionSet.objects.create()
        expset.name = 'Andalve3'
        expset.abbr = 'AND3'
        expset.save()

        fes = FormatExpansionSet.objects.create(format=ff, expansionset=expset)
        fes.save()

        bcard0 = self.load_card(self.black_lotus_json, 'Black Lotus', loadhelper=False, set_abbr='AND3')
        bcard1 = self.load_card(self.cavern_of_souls_json, 'Cavern of Souls', loadhelper=False, set_abbr='AND3')

        self.assertEquals(Card.objects.filter(expansionset=expset).count(), 2)

        self.assertEquals(len(ff.formatexpansionset_set.all()), 1)

        self.assertEquals(len(ff.formatbasecard_set.all()), 0)

        ff.populate_format_cards()

        self.assertEquals(len(ff.formatbasecard_set.all()), 2)

    def test_format_add_expset_proc_wbc(self):
        ff = Format.objects.create()
        ff.format = 'tfae3wbcTest'
        ff.formatname = 'Standard'
        ff.abbr = 'STD'
        ff.start_date = date(year=2017, month=7, day=1)
        ff.end_date = date(year=2017, month=10, day=31)

        ff.save()

        expset = ExpansionSet.objects.create()
        expset.name = 'Andalve4'
        expset.abbr = 'AND4'
        expset.save()

        fes = FormatExpansionSet.objects.create(format=ff, expansionset=expset)
        fes.save()

        bcard0 = self.load_card(self.black_lotus_json, 'Black Lotus', loadhelper=False, set_abbr='AND4')
        bcard1 = self.load_card(self.cavern_of_souls_json, 'Cavern of Souls', loadhelper=False, set_abbr='AND4')

        fbc = FormatBannedCard.objects.create(format=ff, physicalcard=bcard0.physicalcard)
        fbc.save()

        self.assertEquals(Card.objects.filter(expansionset=expset).count(), 2)

        self.assertEquals(len(ff.formatexpansionset_set.all()), 1)

        self.assertEquals(len(ff.formatbasecard_set.all()), 0)

        ff.populate_format_cards()

        self.assertEquals(len(ff.formatbasecard_set.all()), 1)

    def test_format_multi(self):
        ff = Format.objects.create()
        ff.format = 'MultiTest0'
        ff.formatname = 'Standard'
        ff.abbr = 'STD'
        ff.start_date = date(year=2017, month=7, day=1)
        ff.end_date = date(year=2017, month=10, day=31)

        ff.save()

        expset1 = ExpansionSet.objects.create()
        expset1.name = 'MultAndalve1'
        expset1.abbr = 'MAND1'
        expset1.save()
        expset2 = ExpansionSet.objects.create()
        expset2.name = 'MultAndalve2'
        expset2.abbr = 'MAND2'
        expset2.save()
        expset3 = ExpansionSet.objects.create()
        expset3.name = 'MultAndalve3'
        expset3.abbr = 'MAND3'
        expset3.save()

        fes1 = FormatExpansionSet.objects.create(format=ff, expansionset=expset1)
        fes1.save()
        fes2 = FormatExpansionSet.objects.create(format=ff, expansionset=expset2)
        fes2.save()

        bcard0 = self.load_card(self.black_lotus_json, 'Black Lotus', loadhelper=False, set_abbr='MAND1')
        bcard1 = self.load_card(self.cavern_of_souls_json, 'Cavern of Souls', loadhelper=False, set_abbr='MAND1')
        bcard2 = self.load_card(self.plains_json, 'Plains', loadhelper=False, set_abbr='MAND1')
        bcard3 = self.load_card(self.forest_json, 'Forest', loadhelper=False, set_abbr='MAND1')
        bcard4 = self.load_card(self.plains_json, 'Plains', loadhelper=False, set_abbr='MAND2')
        bcard5 = self.load_card(self.island_json, 'Island', loadhelper=False, set_abbr='MAND2')
        bcard6 = self.load_card(self.swamp_json, 'Swamp', loadhelper=False, set_abbr='MAND2')
        bcard7 = self.load_card(self.mountain_json, 'Mountain', loadhelper=False, set_abbr='MAND3')

        fbc = FormatBannedCard.objects.create(format=ff, physicalcard=bcard0.physicalcard)
        fbc.save()

        self.assertEquals(Card.objects.filter(expansionset=expset1).count(), 4)
        self.assertEquals(Card.objects.filter(expansionset=expset2).count(), 3)
        self.assertEquals(Card.objects.filter(expansionset=expset3).count(), 1)

        self.assertEquals(len(ff.formatexpansionset_set.all()), 2)

        self.assertEquals(len(ff.formatbasecard_set.all()), 0)

        ff.populate_format_cards()

        self.assertEquals(len(ff.formatbasecard_set.all()), 5)  # Cavern, Plains, Forest, Island, Swamp
