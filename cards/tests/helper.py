# -*- coding: utf-8 -*-

from cards.models import Color, Rarity, Type, Subtype, PhysicalCard, Card, BaseCard, CardRating, ExpansionSet, Format, FormatBasecard, SearchPredicate, CardType, CardSubtype, CardColor
from cards.models import Supertype, CardSupertype
from datetime import datetime, date
from cards.management.commands import initcardsdatabase

import sys
err = sys.stderr


class TestLoadHelper():

    initer = initcardsdatabase.Command()

    def color_loader(self):
        self.initer.init_colors()

    def rarity_loader(self):
        self.initer.init_rarities()

    def basics_loader(self):
        self.color_loader()
        self.rarity_loader()

        self.supertype_loader()
        self.type_loader()
        self.subtype_loader()
        self.expansionset_example_loader()
        self.format_example_loader()
        self.basic_lands_loader()

    def type_loader(self):
        types = (
            'Artifact',
            'Conspiracy',
            'Creature',
            'Enchantment',
            'Instant',
            'Land',
            'Phenomenon',
            'Plane',
            'Planeswalker',
            'Scheme',
            'Sorcery',
            'Tribal',
            'Vanguard')

        for tt in types:
            tto = Type()
            tto.type = tt
            tto.save()

    def supertype_loader(self):
        supertypes = (
            'Basic',
            'Legendary',
            'Snow',
            'World')

        for st in supertypes:
            sto = Supertype()
            sto.supertype = st
            sto.save()

    def subtype_loader(self):
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

        for st in subtypes:
            sto = Subtype()
            sto.subtype = st
            sto.save()

    def expansionset_example_loader(self):
        esets = [['Sample Expansion Foo', 'FOO', '2017-01-01'],
                 ['Sample Expansion Bar', 'BAR', '2017-04-04']]
        for eset in esets:
            eee = ExpansionSet()
            eee.name = eset[0]
            eee.abbr = eset[1]
            eee.releasedate = eset[2]
            eee.save()

    def format_example_loader(self):
        formats = [['Modern', 'Modern_2014-09-26', datetime(2014, 9, 26), datetime(2015, 1, 22)],
                   ['Standard', 'Standard_2014-09-26', datetime(2014, 9, 26), datetime(2015, 1, 22)],
                   ['Standard', 'Standard_2015-01-23', datetime(2015, 1, 23), datetime(2015, 3, 26)],
                   ['Commander', 'Commander_2015-01-17', datetime(2015, 1, 17), datetime(2015, 3, 26)],
                   ['Modern', 'Modern_2015-01-23', datetime(2015, 1, 23), datetime(2015, 2, 1)],
                   ['Modern', 'Modern_2015-02-01', datetime(2015, 2, 1), datetime(2015, 3, 1)],
                   ['Modern', 'Modern_2015-03-01', datetime(2015, 3, 1), datetime(2015, 4, 1)],
                   ['Modern', 'Modern_2015-04-01', datetime(2015, 4, 1), datetime(2015, 5, 1)],
                   ['Modern', 'Modern_2015-05-01', datetime(2015, 5, 1), datetime(2015, 6, 1)],
                   ]

        for fmat in formats:
            fff = Format()
            fff.formatname = fmat[0]
            fff.format = fmat[1]
            fff.start_date = fmat[2]
            fff.end_date = fmat[3]
            fff.save()

    def basic_lands_loader(self):
        lands = [['Plains', 'w'], ['Island', 'u'], ['Swamp', 'b'], ['Mountain', 'r'], ['Forest', 'g']]

        bl_rarity = Rarity.objects.get(pk='b')
        basic_supertype = Supertype.objects.filter(supertype='Basic').first()
        land_type = Type.objects.filter(type='Land').first()
        color = Color.objects.get(pk='c')
        formats = Format.objects.all()
        expsets = ExpansionSet.objects.all()
        counter = 0
        for landd in lands:
            counter = counter + 1
            pc = PhysicalCard()
            pc.save()
            bc = BaseCard()
            bc.physicalcard = pc
            bc.name = landd[0]
            bc.mana_cost = ''
            bc.cmc = 0
            bc.rules_text = '{t}: Add {' + landd[1] + '}.'
            bc.save()

            cst = CardSupertype()
            cst.basecard = bc
            cst.position = 0
            cst.supertype = basic_supertype
            cst.save()

            ct2 = CardType()
            ct2.basecard = bc
            ct2.position = 0
            ct2.type = land_type
            ct2.save()

            cst = CardSubtype()
            cst.basecard = bc
            cst.position = 0
            cst.subtype = Subtype.objects.filter(subtype=landd[0]).first()
            cst.save()

            cc = CardColor()
            cc.basecard = bc
            cc.color = color
            cc.save()

            # In all expansion sets
            esetcounter = 0
            for eset in expsets:
                esetcounter = esetcounter + 1
                card = Card()
                card.basecard = bc
                card.expansionset = eset
                card.rarity = bl_rarity
                card.multiverseid = (esetcounter * 1000) + counter
                card.card_number = counter
                card.save()

            # In all formats
            for fff in formats:
                fbc = FormatBasecard()
                fbc.basecard = bc
                fbc.format = fff
                fbc.save()
