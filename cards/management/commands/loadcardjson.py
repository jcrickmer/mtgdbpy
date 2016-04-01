from django.core.management.base import BaseCommand, CommandError
from cards.models import PhysicalCard
from cards.models import BaseCard
from cards.models import Card
from cards.models import Color, CardColor
from cards.models import Rarity
from cards.models import Type
from cards.models import Subtype
from cards.models import CardType
from cards.models import CardSubtype
from cards.models import Mark
from cards.models import ExpansionSet
from cards.models import Ruling

import logging
import sys
import os
import json


class Command(BaseCommand):

    help = '''Load up some JSON and add it to the database, if needed.'''

    def add_arguments(self, parser):
        parser.add_argument('input')

    def handle(self, *args, **options):
        #logger = logging.getLogger(__name__)
        # the first (and only) arg should be a filename

        filename = options['input']
        if not os.access(filename, os.R_OK):
            sys.stderr.write("Cannot read file '{}'.\n".format(filename))
            return

        filehandler = open(filename)
        jblob = json.load(filehandler)

        # let's test if jblob is a set JSON
        if 'name' in jblob and 'code' in jblob and 'cards' in jblob:
            sys.stdout.write("File is a set JSON for '{}' ({}) with {} cards.\n".format(jblob['name'], jblob['code'], len(jblob['cards'])))

            expset = self.get_expset(jblob['name'], jblob['code'])
            for jcard in jblob['cards']:
                self.handle_card(jcard, expset)
        # maybe it is AllSets
        elif 'LEA' in jblob and 'code' in jblob['LEA'] and 'cards' in jblob['LEA']:
            sys.stdout.write("File is a AllSets JSON...")
            for expkey in jblob.keys():
                eblob = jblob[expkey]
                try:
                    expset = self.get_expset(eblob['name'], eblob['code'])
                    for jcard in eblob['cards']:
                        self.handle_card(jcard, expset)
                except:
                    sys.stdout.write("COULD NOT get expansionset or handle_card threw an error.\n")
                    pass
        pass

    def get_expset(self, name, code):
        expset = ExpansionSet.objects.filter(abbr=code).first()
        if expset is None:
            expset = ExpansionSet(name=name, abbr=code)
            expset.save()
        return expset

    def handle_card_json(self, card_string, expset):
        jcard = json.loads(card_string)
        return self.handle_card(jcard, expset)

    def handle_card(self, jcard, expset):
        try:
            # First, let's see if we have this basecard
            bc = None
            try:
                bc = BaseCard.objects.get(name=jcard['name'])
                self.update_basecard(jcard, bc)
            except BaseCard.DoesNotExist:
                bc = self.add_basecard(jcard)

            # REVISIT - what about updates to BaseCard?

            # Now let's get the Card
            card = None
            card_number = None
            try:
                card_number = jcard['card_number']
            except KeyError:
                pass
            if card_number is None:
                try:
                    card_number = jcard['number']
                except KeyError:
                    pass

            sys.stderr.write("Name: " + jcard['name'] + ': ')

            try:
                lll = jcard['layout']
                if lll == 'token':
                    sys.stderr.write(" token, so skipped.\n")
                    return
            except KeyError:
                sys.stderr.write(" no layout, so skipped.\n")
                return

            try:
                muid = jcard['multiverseid']
            except KeyError:
                sys.stderr.write(" no multiverseid, so skipped.\n")
                return

            sys.stderr.write(" " + str(jcard['multiverseid']) + '\n')
            # sys.stderr.write(" card #: " + str(card_number) + '\n')
            #sys.stderr.write(str(bc) + "\n")

            card = Card.objects.filter(
                expansionset=expset,
                card_number=card_number,
                multiverseid=jcard['multiverseid'],
                basecard=bc).first()
            if card is None:
                card = self.add_card(jcard, expset, bc)
            else:
                # let's update the card
                card = self.update_card(jcard, card)

            # and now rulings
            self.set_rulings(bc, jcard)
        except:
            try:
                sys.stderr.write("UNABLE TO LOAD CARD: " + jcard['name'] + '\n')
            except KeyError:
                sys.stderr.write("UNABLE TO LOAD CARD WITH NO NAME!!\n")

    def add_basecard(self, jcard):
        # Initially, I had tried to put all of the objecst into a
        # list, and if everthing was good, we would .save() all of the
        # models in the list. Turns out that Django does not support
        # this. See https://code.djangoproject.com/ticket/10811. So I
        # looked at transactions and autocommit. That looks
        # dangerouns, and I don't know how to write all of the test
        # cases around it. So, things are just going to be dirty.

        pc = PhysicalCard()
        pc.layout = pc.NORMAL
        cardposition = 'F'  # FRONT

        card_number = ''
        try:
            card_number = str(jcard['number'])
        except KeyError:
            pass

        try:
            pc.layout = jcard['layout']

            if pc.layout in [pc.DOUBLE, pc.SPLIT, pc.FLIP]:
                # We need to see if we already have a PhysicalCard of the other half of
                # this card. We will leverage the 'names' array to figure this out.
                for other_name in jcard['names']:
                    if other_name == jcard['name']:
                        # this is us. skip us.
                        # continue
                        pass
                    other_bc = BaseCard.objects.filter(name=other_name).first()
                    if other_bc is not None:
                        pc = other_bc.physicalcard
                        pc.layout = jcard['layout']
                    if pc.layout == pc.DOUBLE:
                        if 'a' in card_number or 'A' in card_number:
                            cardposition = 'F'
                        if 'b' in card_number or 'B' in card_number:
                            cardposition = 'B'
                    if pc.layout == pc.SPLIT:
                        if 'a' in card_number or 'A' in card_number:
                            cardposition = BaseCard.LEFT
                        if 'b' in card_number or 'B' in card_number:
                            cardposition = BaseCard.RIGHT
                    if pc.layout == pc.FLIP:
                        if 'a' in card_number or 'A' in card_number:
                            cardposition = 'U'
                        if 'b' in card_number or 'B' in card_number:
                            cardposition = 'D'

        except Error:
            # don't care much...
            pass

        pc.save()

        bc = BaseCard()
        bc.physicalcard = pc
        bc.cardposition = cardposition
        try:
            bc.name = jcard['name']
        except KeyError:
            # REVISIT - we now have an orphaned PhysicalCard
            raise KeyError('JSON is missing attribute "name".')

        try:
            bc.mana_cost = jcard['manaCost']
        except KeyError:
            # REVISIT - we now have an orphaned PhysicalCard
            #raise KeyError('JSON is missing attribute "manaCost".')
            # let's assume that there is no mana cost sometimes. Like on lands. But maybe we should double-check... REVISIT
            pass

        try:
            bc.cmc = jcard['cmc']
        except KeyError:
            # REVISIT - we now have an orphaned PhysicalCard
            #raise KeyError('JSON is missing attribute "cmc".')
            # let's assume that there is no mana cost sometimes. Like on lands. But maybe we should double-check... REVISIT
            pass

        try:
            bc.rules_text = jcard['text']
        except KeyError:
            bc.rules_text = ''

        bc.save()

        if 'types' not in jcard:
            # What, no type?
            raise KeyError('JSON is missing "types".')

        self.update_basecard(jcard, bc)

        return bc

    def update_basecard(self, jcard, bc):

        try:
            bc.rules_text = jcard['text']
        except KeyError:
            bc.rules_text = ''

        try:
            bc.power = jcard['power']
        except KeyError:
            pass
        try:
            bc.toughness = jcard['toughness']
        except KeyError:
            pass
        try:
            bc.loyalty = jcard['loyalty']
        except KeyError:
            pass

        bc.save()

        type_counter = 0
        CardType.objects.filter(basecard=bc).delete()
        for jsontype in ['supertypes', 'types']:
            if jsontype not in jcard:
                continue
            for ctype in jcard[jsontype]:
                # need to see if we know about this type
                dbtype = None
                try:
                    dbtype = Type.objects.get(type=ctype)
                except Type.DoesNotExist:
                    # better add this type!
                    dbtype = self.add_type(ctype)

                ct = CardType()
                ct.basecard = bc
                ct.type = dbtype
                ct.position = type_counter
                ct.save()
                type_counter = type_counter + 1

        try:
            CardSubtype.objects.filter(basecard=bc).delete()
            subtype_counter = 0
            for csubtype in jcard['subtypes']:
                # need to see if we know about this subtype
                dbsubtype = None
                try:
                    dbsubtype = Subtype.objects.get(subtype=csubtype)
                except Subtype.DoesNotExist:
                    # better add this subtype!
                    dbsubtype = self.add_subtype(csubtype)

                cst = CardSubtype()
                cst.basecard = bc
                cst.subtype = dbsubtype
                cst.position = subtype_counter
                cst.save()
                subtype_counter = subtype_counter + 1
        except KeyError:
            pass

        try:
            CardColor.objects.filter(basecard=bc).delete()
            for ccolor in jcard['colors']:
                dbcolor = Color.objects.get(color__iexact=ccolor)
                cc = CardColor()
                cc.basecard = bc
                cc.color = dbcolor
                cc.save()
        except KeyError:
            pass

        return bc

    def add_type(self, cardtype):
        result = Type.objects.create()
        result.type = cardtype
        result.save()
        return result

    def add_subtype(self, cardsubtype):
        result = Subtype.objects.create()
        result.subtype = cardsubtype
        result.save()
        return result

    def add_card(self, jcard, expset, basecard):
        card = Card()
        card.basecard = basecard
        try:
            card.card_number = jcard['number']
        except KeyError:
            pass
        card.expansionset = expset
        card.multiverseid = int(jcard['multiverseid'])
        card.save()

        card = self.update_card(jcard, card)
        return card

    def update_card(self, jcard, card):

        card.rarity = Rarity.objects.filter(rarity__iexact=jcard['rarity']).first()

        try:
            card.flavor_text = jcard['flavor']
        except KeyError:
            pass

        mark = None
        try:
            mark = Mark.objects.filter(mark__iexact=jcard['watermark']).first()
        except KeyError:
            pass
        except Mark.DoesNotExist:
            mark = self.add_mark(jcard['watermark'])
        card.mark = mark

        card.save()
        return card

    def add_mark(self, mark_s):
        result = Mark.objects.create()
        result.mark = mark_s
        result.save()
        return result

    def set_rulings(self, basecard, jcard):
        # delete everything that this there now
        Ruling.objects.filter(basecard=basecard).delete()
        jrulings = list()
        try:
            jrulings = jcard['rulings']
        except KeyError:
            pass
        for jruling in jrulings:
            try:
                ruling = Ruling()
                ruling.basecard = basecard
                ruling.ruling_date = jruling['date']
                ruling.ruling_text = jruling['text']
                ruling.save()
            except KeyError:
                pass
