# -*- coding: utf-8 -*-

from cards.models import PhysicalCard
from cards.models import BaseCard
from cards.models import Card
from cards.models import CardPrice
from cards.models import Color, CardColor
from cards.models import Rarity
from cards.models import Type
from cards.models import Supertype
from cards.models import Subtype
from cards.models import CardType
from cards.models import CardSupertype
from cards.models import CardSubtype
from cards.models import Mark
from cards.models import ExpansionSet
from cards.models import Ruling
from django.db.models import Q
from django.utils import dateparse

import logging
import sys
#import traceback
import os
import json

logger = logging.getLogger(__name__)


class CardDataError(BaseException):
    pass


class CardMissingNameError(CardDataError):
    pass


class CardMissingLayoutError(CardDataError):
    pass


class CardMissingMultiverseIdError(CardDataError):
    pass


class Processor(object):

    '''Load up some JSON and add it to the database, if needed.'''

    def __init__(self, filename=None):
        self.filename = filename

    def process(self):
        if not os.access(self.filename, os.R_OK):
            raise(FileNotFoundError("Cannot read file '{}'".format(self.filename)))

        filehandler = open(self.filename)

        # This could throw a parseing error, I believe. That is ok.
        jblob = json.load(filehandler)

        # let's test if jblob is a set JSON
        if 'name' in jblob and 'code' in jblob and 'cards' in jblob:
            cards_to_load_count = len(jblob['cards'])
            logger.info("File is a set JSON for '{}' ({}) with {} cards.\n".format(jblob['name'], jblob['code'], cards_to_load_count))

            reldate = None
            if 'releaseDate' in jblob:
                reldate = jblob['releaseDate']

            expset = self.get_expset(jblob['name'], jblob['code'], reldate)

            percent_complete = 0.0
            cards_added_or_updated_count = 0
            card_process_count = 0
            for jcard in jblob['cards']:
                try:
                    card = self.handle_card(jcard, expset)
                    card_process_count += 1
                    percent_complete = float(card_process_count) / float(cards_to_load_count)
                    cards_added_or_updated_count += 1
                    logger.info(
                        "Loaded card \"{}\" {} from \"{}\". [{} of {} = {:.2f}% complete]".format(
                            card.basecard.name,
                            card.card_number,
                            card.expansionset.name,
                            card_process_count,
                            cards_to_load_count,
                            100.0 * percent_complete))

                except CardMissingLayoutError as cmle:
                    logger.info("\"{}\" does not have a layout. Not processed.".format(jcard['name']))
                except CardMissingMultiverseIdError as cmmuide:
                    logger.info("\"{}\" does not have a multiverseId. Not processed.".format(jcard['name']))

        # maybe it is AllSets
        elif 'LEA' in jblob and 'code' in jblob['LEA'] and 'cards' in jblob['LEA']:
            raise(NotImplementedError("JSON file is NOT a set JSON file. This isn't implemented yet."))
            #sys.stdout.write("File is a AllSets JSON...")
            for expkey in jblob.keys():
                eblob = jblob[expkey]
                try:
                    reldate = None
                    if 'releaseDate' in eblob:
                        reldate = eblob['releaseDate']
                    expset = self.get_expset(eblob['name'], eblob['code'], reldate)
                    sys.stderr.write("The expset is {}\n".format(expset))
                    for jcard in eblob['cards']:
                        self.handle_card(jcard, expset)
                except BaseException as e:
                    sys.stdout.write("COULD NOT get expansionset or handle_card threw an error.\n")
                    sys.stdout.write(str(e))
                    pass
        else:
            raise(NotImplementedError("Unable to get anything meaningful from JSON file. This isn't implemented yet."))

    def get_expset(self, name, code, releasedate):
        expset = ExpansionSet.objects.filter(abbr=code).first()
        if expset is None:
            expset = ExpansionSet(name=name, abbr=code, releasedate=releasedate)
            expset.save()
        elif releasedate is not None:
            # Let's update release date just in case
            expset.releasedate = releasedate
            expset.save()
        return expset

    def handle_card_json(self, card_string, expset):
        ''' Short-cut to just run handle_card.
        '''
        jcard = json.loads(card_string)
        return self.handle_card(jcard, expset)

    def handle_card(self, jcard, expset):
        try:
            if jcard['layout'] == 'token':
                raise(CardMissingLayoutError)
        except KeyError:
            raise(CardMissingLayoutError)

        try:
            muid = self.get_muid(jcard)
        except KeyError:
            raise(CardMissingMultiverseIdError)

        try:
            cardname = jcard['name']
        except KeyError:
            raise(CardMissingNameError)

        # First, let's see if we have this basecard
        bc = None
        try:
            name_ashremoved = jcard['name'].replace(u'\u00C6', 'Ae')
            name_ashremoved = name_ashremoved.replace(u'\u00E6', 'ae')
            #sys.stderr.write("L79 Name: " + name_ashremoved + "\n")
            bc = BaseCard.objects.filter(Q(name=jcard['name']) | Q(name=name_ashremoved)).first()
            if bc is None:
                raise BaseCard.DoesNotExist()
                #sys.stderr.write("L81 bc is: {}\n".format(bc))
            self.update_basecard(jcard, bc)
        except BaseCard.DoesNotExist:
            bc = self.add_basecard(jcard)
        # some other exception or error could be thrown. Let it bubble up.

        # REVISIT - what about updates to BaseCard?

        # Now let's get the Card
        card = None
        card_number = self.get_card_number(jcard)

        #sys.stderr.write("Name: " + jcard['name'] + ': ')

        card = Card.objects.filter(expansionset=expset,
                                   card_number=card_number,
                                   multiverseid=self.get_muid(jcard),
                                   basecard=bc).first()
        if card is None:
            card = self.add_card(jcard, expset, bc)
        else:
            # let's update the card
            card = self.update_card(jcard, card)

        # and now rulings
        self.set_rulings(bc, jcard)

        # let's set prices...
        if 'prices' in jcard:
            if 'paper' in jcard['prices']:
                for pdate in jcard['prices']['paper']:
                    try:
                        cprice = float(jcard['prices']['paper'][pdate])
                    except ValueError:
                        logger.warning(
                            "Unable to save card price for \"{}\" with date \"{}\" and price \"{}\" because it isn't a number.".format(
                                card.basecard.name, pdate, jcard['prices']['paper'][pdate]))
                        continue
                    dt = dateparse.parse_datetime('{}T00:00:00+00:00'.format(pdate))
                    if dt is not None:
                        try:
                            card_price, created = CardPrice.objects.get_or_create(card_id=card.id, printing='normal', at_datetime=dt)
                            if created or card_price.price != cprice:
                                card_price.price = cprice
                                card_price.save()
                        except BaseException as be:
                            # probably a SQL error?
                            logger.warning(
                                "Unable to save card price for \"{}\" with date \"{}\" and price \"{}\". Exception: {}".format(
                                    card.basecard.name, pdate, cprice, be))
                            pass
        return card

    def get_card_number(self, jcard):
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
        if 'side' in jcard and 'a' not in card_number and 'b' not in card_number and 'c' not in card_number and 'd' not in card_number and 'e' not in card_number:
            card_number = '{}{}'.format(card_number, jcard['side']).lower()
        return card_number

    def get_muid(self, jcard):
        if 'multiverseid' in jcard:
            result = jcard['multiverseid']
        else:
            result = jcard['multiverseId']
        return int(result)

    def add_basecard(self, jcard):
        # Initially, I had tried to put all of the objects into a
        # list, and if everything was good, we would .save() all of the
        # models in the list. Turns out that Django does not support
        # this. See https://code.djangoproject.com/ticket/10811. So I
        # looked at transactions and autocommit. That looks
        # dangerous, and I don't know how to write all of the test
        # cases around it. So, things are just going to be dirty.

        pc = PhysicalCard()
        # MTGJSON now includes layout... maybe I should leverage their data here.
        pc.layout = pc.NORMAL
        cardposition = BaseCard.FRONT

        card_number = self.get_card_number(jcard)

        try:
            pc.layout = jcard['layout']

            if pc.layout in [pc.DOUBLE, pc.SPLIT, pc.FLIP, pc.AFTERMATH]:
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
                    if pc.layout in (pc.FLIP, pc.AFTERMATH):
                        if 'a' in card_number or 'A' in card_number:
                            cardposition = 'U'
                        if 'b' in card_number or 'B' in card_number:
                            cardposition = 'D'

        except BaseException:
            # don't care much...
            pass

        pc.save()

        bc = BaseCard()
        bc.physicalcard = pc
        bc.cardposition = cardposition

        # Name is going to be handled by update_basecard anyway...
        try:
            bc.name = jcard['name']
        except KeyError:
            # REVISIT - we now have an orphaned PhysicalCard
            raise KeyError('JSON is missing attribute "name".')

        # Rules text is going to be handled by update_basecard anyway...
        # try:
        #    bc.rules_text = jcard['text']
        # except KeyError:
        #    bc.rules_text = ''

        bc.save()

        self.update_basecard(jcard, bc)

        return bc

    def update_basecard(self, jcard, bc):

        try:
            bc.name = jcard['name']
        except KeyError:
            # REVISIT - we now have an orphaned PhysicalCard
            raise KeyError('JSON is missing attribute "name".')

        try:
            bc.rules_text = jcard['text']
        except KeyError:
            bc.rules_text = ''
        if len(bc.rules_text) < 1:
            if jcard['name'] == 'Plains':
                bc.rules_text = '{T}: Add {W} to your mana pool.'
            elif jcard['name'] == 'Island':
                bc.rules_text = '{T}: Add {U} to your mana pool.'
            elif jcard['name'] == 'Swamp':
                bc.rules_text = '{T}: Add {B} to your mana pool.'
            elif jcard['name'] == 'Mountain':
                bc.rules_text = '{T}: Add {R} to your mana pool.'
            elif jcard['name'] == 'Forest':
                bc.rules_text = '{T}: Add {G} to your mana pool.'
            elif jcard['name'] == 'Wastes':
                bc.rules_text = '{T}: Add {C} to your mana pool.'

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

        try:
            bc.mana_cost = jcard['manaCost']
        except KeyError:
            # REVISIT - we now have an orphaned PhysicalCard
            #raise KeyError('JSON is missing attribute "manaCost".')
            # let's assume that there is no mana cost sometimes. Like on lands. But maybe we should double-check... REVISIT
            pass

        try:
            if 'cmc' in jcard:
                bc.cmc = jcard['cmc']
            else:
                bc.cmc = int(jcard['convertedManaCost'])
        except KeyError:
            # REVISIT - we now have an orphaned PhysicalCard
            #raise KeyError('JSON is missing attribute "cmc".')
            # let's assume that there is no mana cost sometimes. Like on lands. But maybe we should double-check... REVISIT
            pass

        sptype_counter = 0
        CardSupertype.objects.filter(basecard=bc).delete()
        if 'supertypes' in jcard:
            for csptype in jcard['supertypes']:
                # need to see if we know about this supertype
                dbsptype = None
                try:
                    dbsptype = Supertype.objects.get(supertype=csptype)
                except Supertype.DoesNotExist:
                    # better add this type!
                    dbsptype = self.add_supertype(csptype)

                cspt = CardSupertype()
                cspt.basecard = bc
                cspt.supertype = dbsptype
                cspt.position = sptype_counter
                cspt.save()
                sptype_counter = sptype_counter + 1

        is_perm = False
        type_counter = 0
        CardType.objects.filter(basecard=bc).delete()
        if 'types' in jcard:
            for ctype in jcard['types']:
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
                ctypel = ctype.lower()
                is_perm = is_perm or ctypel in ['artifact', 'creature', 'enchantment', 'land', 'planeswalker']

        bc.ispermanent = is_perm

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
                try:
                    dbcolor = Color.objects.get(color__iexact=ccolor)
                except Color.DoesNotExist:
                    dbcolor = Color.objects.get(id__iexact=ccolor)
                cc = CardColor()
                cc.basecard = bc
                cc.color = dbcolor
                cc.save()
        except KeyError:
            pass

        bc.save()

        return bc

    def add_type(self, cardtype):
        result = Type.objects.create()
        result.type = cardtype
        result.save()
        return result

    def add_supertype(self, cardsupertype):
        result = Supertype.objects.create()
        result.supertype = cardsupertype
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
        card.card_number = self.get_card_number(jcard)
        card.expansionset = expset
        card.multiverseid = self.get_muid(jcard)
        card.save()

        card = self.update_card(jcard, card)
        return card

    def update_card(self, jcard, card):

        # Looks like MTGJSON changed 'Mythic' to 'Mythic Rare', or something like that.
        card.rarity = Rarity.objects.filter(rarity__istartswith=jcard['rarity'][0:3]).first()

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
