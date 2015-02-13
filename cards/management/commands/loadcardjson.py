from django.core.management.base import BaseCommand, CommandError
from cards.models import PhysicalCard
from cards.models import BaseCard
from cards.models import Card
from cards.models import Color
from cards.models import Rarity
from cards.models import Type
from cards.models import Subtype
from cards.models import CardType
from cards.models import CardSubtype
from cards.models import Mark


import logging
import sys

import json

class Command(BaseCommand):

    help = '''Load up some JSON and add it to the database, if needed.'''

    def handle(self, *args, **options):
        #logger = logging.getLogger(__name__)
        pass

    def handle_card_json(self, card_string, expset):

        jcard = json.loads(card_string)

        # First, let's see if we have this basecard
        bc = None
        try:
            bc = BaseCard.objects.get(name=jcard['name'])
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
        card = Card.objects.filter(expansionset=expset, card_number=card_number, multiverseid=jcard['multiverseid'],basecard=bc).first()
        if card is None:
            card = self.add_card(jcard, expset, bc)
 
        # REVISIT - what about updates to Card?

        #sys.stderr.write("Name: " + jcard['name'] + '\n')
        #sys.stderr.write("MUID: " + str(card.multiverseid) + '\n')
        #sys.stderr.write(str(bc) + "\n")

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
        cardposition = 'F' #FRONT

        card_number = ''
        try:
            card_number = str(jcard['number'])
        except KeyError:
            pass

        try:
            pc.layout = jcard['layout']
            if pc.layout in [pc.DOUBLE, pc.SPLIT, pc.FLIP]:
                # We need to see if we already have a PhysicalCard of the other half of this card. We will leverage the 'names' array to figure this out.
                for other_name in jcard['names']:
                    if other_name == jcard['name']:
                        # this is us. skip us.
                        continue
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
                                cardposition = 'L'
                            if 'b' in card_number or 'B' in card_number:
                                cardposition = 'R'
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

        type_counter = 0
        for jsontype in ['supertypes','types']:
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
        card.rarity = Rarity.objects.filter(rarity__iexact=jcard['rarity']).first()
        card.multiverseid = int(jcard['multiverseid'])
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
