from django.test import TestCase, TransactionTestCase
from cards.models import Color, Rarity, Type, Subtype, PhysicalCard, Card, BaseCard, CardRating, ExpansionSet, FormatBasecard, SearchPredicate, Format
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction

from cards.tests.helper import TestLoadHelper

import sys
err = sys.stderr

# Create your tests here.


class HelperTestCase(TestCase):

    def test_colors(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        white = Color.objects.get(pk='W')
        blue = Color.objects.get(pk='U')
        black = Color.objects.get(pk='B')
        red = Color.objects.get(pk='R')
        green = Color.objects.get(pk='G')
        colorless = Color.objects.get(pk='c')
        colors = Color.objects.all()
        self.assertEqual(len(colors), 6)

    def test_rarities(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

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

    def test_types(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        types = (
            'Artifact',
            'Basic',
            'Conspiracy',
            'Creature',
            'Enchantment',
            'Instant',
            'Land',
            'Legendary',
            'Ongoing',
            'Phenomenon',
            'Plane',
            'Planeswalker',
            'Scheme',
            'Snow',
            'Sorcery',
            'Tribal',
            'Vanguard',
            'World')
        dbtypes = Type.objects.all().order_by('type')
        self.assertEqual(dbtypes.count(), len(types))
        for ttt in dbtypes:
            self.assertTrue(ttt.type in types)

    def test_subtypes(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        subtypes = (
            'Aura',
            'Human',
            'Goblin',
            'Wizard',
            'Dragon',
            'Elf',
            'Cleric',
            'Warrior',
            'Curse',
            'Soldier',
            'Sphinx',
            'Ajani',
            'Urza\'s',
            'Wurm',
            'Zombie',
            'Chandral',
            'Swamp',
            'Plains',
            'Island',
            'Forest',
            'Mountain',
            'Rat')
        dbsubtypes = Subtype.objects.all().order_by('subtype')
        self.assertEqual(dbsubtypes.count(), len(subtypes))
        for ttt in dbsubtypes:
            self.assertTrue(ttt.subtype in subtypes)

    def test_formats(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        aformats = Format.objects.all()
        self.assertEquals(aformats.count(), 5)

    def test_expansionsets(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        asets = ExpansionSet.objects.all()
        self.assertEquals(asets.count(), 2)

    def test_physicalcards(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        pcs = PhysicalCard.objects.all()
        self.assertEquals(pcs.count(), 5)
        for pc in pcs:
            self.assertEquals(pc.layout, pc.NORMAL)

    def test_basecards(self):
        tlh = TestLoadHelper()
        tlh.basics_loader()

        names = ['Forest', 'Island', 'Mountain', 'Plains', 'Swamp']
        bcs = BaseCard.objects.all().order_by('filing_name')
        self.assertEquals(bcs.count(), 5)
        counter = 0
        for bc in bcs:
            self.assertEquals(bc.name, names[counter])
            self.assertEquals(bc.cmc, 0)
            counter = counter + 1
