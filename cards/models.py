# -*- coding: utf-8 -*-

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals
import sys
import re
from django.conf import settings
from django.db import models
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

from cards.view_utils import convertSymbolsToHTML
from cards.text_utils import filing_string, remove_punctuation
from django.utils.safestring import mark_safe

from django.db.models import Max, Min, Count, Avg
from django.db import connection, ProgrammingError

from django.db.models.functions import TruncDay

import logging
from operator import itemgetter

from django.core.cache import cache

logger = logging.getLogger(__name__)

import time


class Color(models.Model):
    id = models.CharField(primary_key=True, max_length=1)
    color = models.CharField(max_length=9)

    class Meta:
        managed = True
        db_table = 'color'

    def __unicode__(self):
        return self.color


class Rarity(models.Model):
    id = models.CharField(primary_key=True, max_length=1)
    rarity = models.CharField(max_length=11)
    sortorder = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'rarity'
        verbose_name_plural = 'Rarities'

    def __unicode__(self):
        return self.rarity


class Type(models.Model):
    #id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=128, unique=True)
    sort_order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'type'

    def __unicode__(self):
        return self.type


class Supertype(models.Model):
    #id = models.IntegerField(primary_key=True)
    supertype = models.CharField(max_length=128, unique=True)

    class Meta:
        managed = True
        db_table = 'supertype'

    def __unicode__(self):
        return self.supertype


class Subtype(models.Model):
    #id = models.IntegerField(primary_key=True)
    subtype = models.CharField(max_length=128, unique=True)

    class Meta:
        managed = True
        db_table = 'subtype'

    def __unicode__(self):
        return self.subtype


class PhysicalCard(models.Model):
    #id = models.IntegerField(primary_key=True)
    NORMAL = 'normal'
    SPLIT = 'split'
    FLIP = 'flip'
    AFTERMATH = 'aftermath'
    DOUBLE = 'double-faced'
    TOKEN = 'token'
    PLANE = 'plane'
    SCHEME = 'scheme'
    PHENOMENON = 'phenomenon'
    LEVELER = 'leveler'
    VANGUARD = 'vanguard'
    LAYOUT_CHOICES = (
        (NORMAL,
         'normal'),
        (SPLIT,
         'split'),
        (FLIP,
         'flip'),
        (AFTERMATH,
         'aftermath'),
        (DOUBLE,
         'double-faced'),
        (TOKEN,
         'token'),
        (PLANE,
         'plane'),
        (SCHEME,
         'scheme'),
        (PHENOMENON,
         'phenomenon'),
        (LEVELER,
         'leveler'),
        (VANGUARD,
         'vanguard'))
    layout = models.CharField(
        max_length=12,
        choices=LAYOUT_CHOICES,
        default=NORMAL)

    def get_cardratings(self, start_date=timezone.now(), end_date=timezone.now()):
        """ Shortcut to get the CardRating for a given Format for this PhysicalCard.

        This is meant to be accessible in templates for display.

        Arguments:
        start_date -- datetime.datetime object that represents the start of the Format search.
        end_date -- datetime.datetime object that represents the last day of the Format search.

        Returns: QuerySet of CardRating objects, ordered by Format.formatname.
        """
        return self.cardrating_set.filter(
            format__start_date__lte=start_date,
            format__end_date__gt=end_date).order_by('format__formatname')

    def get_last_updated(self):
        return max(bc.updated_at for bc in self.basecard_set.all())

    def get_card_name(self):
        first_card = None
        sec_card = None
        for bc in self.basecard_set.all():
            if bc.cardposition == BaseCard.BACK or bc.cardposition == BaseCard.RIGHT or bc.cardposition == BaseCard.DOWN:
                sec_card = bc
            else:
                first_card = bc
        if not first_card:
            result = "!FIRST_CARD MISSING!"
            logger.warning("NO first_card for " + str(self.id))
        else:
            result = first_card.name
        if sec_card:
            result = result + '/' + sec_card.name
        return result

    def get_card_filing_name(self):
        first_card = None
        sec_card = None
        for bc in self.basecard_set.all():
            if bc.cardposition == BaseCard.BACK or bc.cardposition == BaseCard.RIGHT or bc.cardposition == BaseCard.DOWN:
                sec_card = bc
            else:
                first_card = bc
        result = first_card.filing_name
        if sec_card:
            result = result + '/' + sec_card.filing_name
        return result

    def get_face_basecard(self):
        basecard = BaseCard.objects.filter(physicalcard_id=self.id, cardposition__in=[BaseCard.FRONT, BaseCard.LEFT, BaseCard.UP]).first()
        return basecard

    def isOrphan(self):
        return self.basecard_set.all().count() == 0

    def get_latest_card(self):
        """ Returns a Card object for this Physical card.
        """
        card = cache.get('c_pc' + str(self.id))
        if card is None:
            bc = self.basecard_set.filter(cardposition__in=[BaseCard.FRONT, BaseCard.LEFT, BaseCard.UP]).first()
            if bc is None:
                logger.error("PhysicalCard.get_latest_card: ouch. bc is None. PhysicalCard pk={}".format(self.pk))
            card = bc.card_set.all().order_by('-multiverseid').first()
            cache.set('c_pc' + str(self.id), card, settings.CARDS_SEARCH_CACHE_TIME)
        return card

    def get_latest_url_part(self):
        card = self.get_latest_card()
        return str(card.multiverseid) + '-' + card.url_slug()

    def get_searchable_document_selfref_nosymbols(self):
        return self.get_searchable_document(include_names=False, include_symbols=False)

    def get_searchable_document_selfref(self):
        return self.get_searchable_document(include_names=False)

    def get_searchable_document(self, include_names=True, include_symbols=True):
        cache_key = 'pc-{}-searchable-doc-{}-{}'.format(self.id, include_names, include_symbols)
        # 18 hours
        return cache.get_or_set(
            cache_key,
            self._get_searchable_document_nocache(
                include_names=include_names,
                include_symbols=include_symbols),
            60 * 60 * 18)

    def get_es_searchable_document(self, include_names=True, include_symbols=True):
        cache_key = 'pc-{}-es-searchable-doc-{}-{}'.format(self.id, include_names, include_symbols)
        # 18 hours
        result = cache.get(cache_key)
        if not result:
            bdoc = self._get_searchable_document_nocache(include_names=include_names, include_symbols=include_symbols)
            result = dict()
            result['card'] = bdoc
            result['_update_datetime'] = timezone.now().isoformat()
            result['name'] = self.get_card_name()
            result['cmc'] = self.get_face_basecard().cmc
            # put the power and toughness in there, if we have some.
            for bc in self.basecard_set.all():
                try:
                    power = bc.power
                    power = power.replace('*', '4')
                    if 'power' in result:
                        result['power'] = max(eval(power), result['power'])
                    else:
                        result['power'] = eval(power)
                except BaseException:
                    pass
                try:
                    toughness = bc.toughness
                    toughness = toughness.replace('*', '4')
                    if 'toughness' in result:
                        result['toughness'] = max(eval(toughness), result['toughness'])
                    else:
                        result['toughness'] = eval(toughness)
                except BaseException:
                    pass
            result['filing_name'] = self.get_card_filing_name()
            cache.set(cache_key, result, 60 * 60 * 18)
        return result

    def get_highest_power_as_int(self):
        result = None
        for bc in self.basecard_set.all():
            try:
                power = bc.power
                power = power.replace('*', '4')
                result = max(eval(power), result)
            except BaseException:
                pass
        return result

    def get_highest_toughness_as_int(self):
        result = None
        for bc in self.basecard_set.all():
            try:
                toughness = bc.toughness
                toughness = toughness.replace('*', '4')
                result = max(eval(toughness), result)
            except BaseException:
                pass
        return result

    def get_searchable_document_rules(self, include_names=True, include_symbols=True):
        result = ''

        for basecard in self.basecard_set.all():
            if include_names:
                result = result + basecard.filing_name + "\n"
            rules = basecard.rules_text
            if rules is None or len(rules) == 0:
                if basecard.name == 'Plains':
                    rules = 'tap: add manawhite to your mana pool.'
                elif basecard.name == 'Island':
                    rules = 'tap: add manablue to your mana pool.'
                elif basecard.name == 'Swamp':
                    rules = 'tap: add manablack to your mana pool.'
                elif basecard.name == 'Mountain':
                    rules = 'tap: add manared to your mana pool.'
                elif basecard.name == 'Forest':
                    rules = 'tap: add managreen to your mana pool.'
                elif basecard.name == 'Waste':
                    rules = 'tap: add manacolorless to your mana pool.'
            rules = rules.replace(basecard.name, 'cardselfreference')
            rules = rules.replace(':', ' activatedability ')
            rules = rules.replace('When ', 'when triggeredability ')
            rules = rules.replace('Whenever ', 'whenever triggeredability ')
            rules = rules.replace('At ', 'at triggeredability ')
            rules = rules.replace(' when ', ' when triggeredability ')
            rules = rules.replace(' whenever ', ' whenever triggeredability ')
            rules = rules.replace(' at ', ' at triggeredability ')
            rules = rules.lower()
            rules = rules.replace('{c}', ' manacolorless ')
            rules = rules.replace('{t}', ' tap ')
            rules = rules.replace('{e}', ' energy ')
            rules = rules.replace('{q}', ' untap ')
            rules = rules.replace('{w}', ' manawhite ')
            rules = rules.replace('{u}', ' manablue ')
            rules = rules.replace('{b}', ' manablack ')
            rules = rules.replace('{r}', ' manared ')
            rules = rules.replace('{g}', ' managreen ')
            rules = rules.replace('{s}', ' snowsymbol ')
            rules = rules.replace('{x}', ' manax ')
            for numm in range(0, 20):
                rules = rules.replace('{' + str(numm) + '}', 'mana' + str(numm))
            rules = rules.replace("{w/p}", ' manawhite manaphyrexian ')
            rules = rules.replace("{u/p}", ' manablue manaphyrexian ')
            rules = rules.replace("{b/p}", ' manablack manaphyrexian ')
            rules = rules.replace("{r/p}", ' manared manaphyrexian ')
            rules = rules.replace("{g/p}", ' managreen manaphyrexian ')
            rules = rules.replace("{2w}", ' manaalt2 manawhite ')
            rules = rules.replace("{2u}", ' manaalt2 manablue ')
            rules = rules.replace("{2b}", ' manaalt2 manablack ')
            rules = rules.replace("{2r}", ' manaalt2 manared ')
            rules = rules.replace("{2g}", ' manaalt2 managreen ')
            rules = rules.replace("{wu}", ' manawhite manablue manahybrid ')
            rules = rules.replace("{wb}", ' manawhite manablack manahybrid ')
            rules = rules.replace("{ub}", ' manablue manablack manahybrid ')
            rules = rules.replace("{ur}", ' manablue manared manahybrid ')
            rules = rules.replace("{br}", ' manablack manared manahybrid ')
            rules = rules.replace("{bg}", ' manablack managreen manahybrid ')
            rules = rules.replace("{rg}", ' manared managreen manahybrid ')
            rules = rules.replace("{rw}", ' manared manawhite manahybrid ')
            rules = rules.replace("{gw}", ' managreen manawhite manahybrid ')
            rules = rules.replace("{gu}", ' managreen manablue manahybrid ')
            rules = rules.replace("his or her", "thirdpersonsingular")

            result = result + rules + "\n"

        # repacle numbers that have plus and minus signs in front of them.
        pattern = re.compile(r'\+([Xx\d]+)')
        result = pattern.sub(lambda m: 'plus{}'.format(m.group(1)), result)
        pattern = re.compile(r'[\-−\u2010-\u2015]([Xx\d]+)', re.U)
        result = pattern.sub(lambda m: u'minus{}'.format(m.group(1)), result)

        result = result.replace(" or ", " litor ")
        result = result.replace(" and ", " litand ")

        remindpat = re.compile(r'\([^\)]+\)', re.U)
        result = remindpat.sub('', result)

        if not include_symbols:
            result = remove_punctuation(result)
        result = result.replace("\n", ' ')
        return result

    def get_searchable_document_color(self):
        result = ''
        for basecard in self.basecard_set.all():
            # add the pips that are in the mana cost
            if len(basecard.mana_cost) > 0:
                costparts = basecard.mana_cost.lower().split('}')
                for pippart in costparts:
                    if pippart.find('w') > -1:
                        result = result + 'pipwhite '
                    if pippart.find('u') > -1:
                        result = result + 'pipblue '
                    if pippart.find('b') > -1:
                        result = result + 'pipblack '
                    if pippart.find('r') > -1:
                        result = result + 'pipred '
                    if pippart.find('g') > -1:
                        result = result + 'pipgreen '
                    if pippart.find('c') > -1:
                        result = result + 'pipcolorless '
                result = result + "\n"

            uses_pmana = False
            try:
                basecard.rules_text.lower().index('/p}')
                uses_pmana = True
            except ValueError:
                pass
            try:
                basecard.mana_cost.lower().index('/p}')
                uses_pmana = True
            except ValueError:
                pass
            if uses_pmana:
                result = result + " manaphyrexian\n"

            colors = basecard.colors.all()
            if len(colors) > 1:
                result = result + " multicolored\n"
            else:
                result = result + "notmulticolored\n"
            allcolors = ['white', 'blue', 'black', 'red', 'green', 'colorless']
            iscolorless = True
            for color in colors:
                iscolorless = False
                result = result + 'cardcolor' + color.color.lower() + "\n"
                allcolors.remove(color.color.lower())
            for notcolor in allcolors:
                if notcolor != 'colorless':
                    result = result + 'notcardcolor' + notcolor + "\n"
            if iscolorless:
                result = result + "cardcolorcolorless\n"
            else:
                result = result + "notcardcolorcolorless\n"
        return result

    def get_searchable_document_manacost(self):
        result = ''
        strippedcost = ''
        combocmc = 0
        cmcct = 0
        for basecard in self.basecard_set.all():
            cmcct = cmcct + 1
            combocmc = combocmc + basecard.cmc
            result = result + 'cmc' + str(basecard.cmc) + "\n"
            strippedcost = strippedcost + str(basecard.mana_cost)
        if cmcct > 1:
            result = result + 'cmc' + str(combocmc) + "\n"
        strippedcost = strippedcost.replace('{', '')
        # REVISIT - Came across this 'issue', but not sure where it has shown itself, or if it is a bug at all. Sure
        # looks like a bug. Commented out for now.
        #strippedcost = str(basecard.mana_cost).replace('{', '')
        strippedcost = strippedcost.replace('}', '')
        strippedcost = strippedcost.replace('/p', '')
        strippedcost = strippedcost.replace('2/', '')
        strippedcost = strippedcost.replace('/', '')
        result = result + 'manacost' + strippedcost.lower() + "\n"

        return result

    def get_searchable_document_types(self):
        result = ''
        for basecard in self.basecard_set.all():
            if basecard.ispermanent:
                result = result + "ispermanent\n"
            else:
                result = result + "isnotpermanent\n"
            result = result + ' '.join('supertype' + csptype.supertype for csptype in basecard.supertypes.all()) + "\n"
            result = result + ' '.join('type' + ctype.type for ctype in basecard.types.all()) + "\n"
            result = result + ' '.join('subtype' + cstype.subtype for cstype in basecard.subtypes.all()) + "\n"

        return result

    def _get_searchable_document_nocache(self, include_names=True, include_symbols=True):
        result = ''
        result = result + self.get_searchable_document_rules(include_names, include_symbols) + ' '
        result = result + self.get_searchable_document_color() + ' '
        result = result + self.get_searchable_document_manacost() + ' '
        result = result + self.get_searchable_document_types() + ' '
        result = ' '.join(result.split())
        for basecard in self.basecard_set.all():
            # need to add something that does a regexp match on hybrid mana in mana cost and rules text and adds a term for 'manahybrid'

            #result = result + basecard.mana_cost + "\n"

            if basecard.power is not None:
                try:
                    result = result + ' power' + str(basecard.power) + "\n"
                except BaseException:
                    pass
            if basecard.toughness is not None:
                try:
                    result = result + ' toughness' + str(basecard.toughness) + "\n"
                except BaseException:
                    pass
            if basecard.loyalty is not None:
                try:
                    result = result + ' loyalty' + str(basecard.loyalty) + "\n"
                except BaseException:
                    pass

            result = result + "\n"

        result = result + ' layout' + self.layout + "\n"
        if self.basecard_set.all().count() > 1:
            result = " multicard\n" + result

        if not include_symbols:
            result = remove_punctuation(result)

        return result.lower()

    def find_similar_card_ids(self, max_results=18, include_query_card=False):
        from .search import searchservice, midboost, stopwords, keywords, exclude_words, key_phrases, cardtypes

        phrase = self.get_searchable_document_selfref()
        #sys.stderr.write("find_similar_cards_ids with phrase\"{}\"\n".format(phrase))
        qq = {"query": {}}
        queryd = {
            "query": {
                "bool": {
                    "should": [],
                    "must_not": []
                }
            }
        }
        qq['query']["function_score"] = {
            "functions": [
                {
                    "exp": {
                        "cmc": {
                            "origin": self.get_face_basecard().cmc,
                            "scale": 1,
                            "decay": 0.85
                        }
                    }
                }
            ]
        }
        hpower = self.get_highest_power_as_int()
        if hpower is not None:
            powerdist = {
                "gauss": {
                    "power": {
                        "origin": hpower,
                        "scale": 1,
                        "decay": 0.95
                    }
                }
            }
            qq['query']["function_score"]['functions'].append(powerdist)
        htough = self.get_highest_toughness_as_int()
        if htough is not None:
            toughdist = {
                "gauss": {
                    "toughness": {
                        "origin": htough,
                        "scale": 1,
                        "decay": 0.95
                    }
                }
            }
            qq['query']["function_score"]['functions'].append(toughdist)

        if not include_query_card:
            queryd['query']['bool']['must_not'].append({"term": {"_id": str(self.pk)}})

        iamtypeslist = []
        for term in phrase.split():
            term = term.replace('.', '')
            if term in cardtypes:
                iamtypeslist.append(term)
            if term not in exclude_words and term not in stopwords and not term.startswith('cmc'):
                # BOOKMARK - exclude the "cmc3" terms at this time... trying to solve this with cmc field
                match = {"match": {"card": term}}

                if term in midboost:
                    match['match']['card'] = {
                        "query": term,
                        "boost": 2
                    }
                elif term in keywords or term in cardtypes:
                    match['match']['card'] = {
                        "query": term,
                        "boost": 4
                    }

                queryd['query']['bool']['should'].append(match)
        for ct in cardtypes:
            if ct not in iamtypeslist:
                kpmatch = {"match": {"card": {'query': ct, 'boost': -1.1}}}
                queryd['query']['bool']['should'].append(kpmatch)

        # let's try word bigrams...
        rules_text = self.get_searchable_document_rules(include_names=False, include_symbols=False)
        bigrams = []
        rwords = rules_text.split()
        for rwit, rword in enumerate(rwords):
            # do not make bigrams across sentences.
            if '.' not in rword:
                try:
                    next_word = rwords[rwit + 1]
                    next_word = next_word.replace('.', '')
                    pboost = 1.0
                    if rword not in stopwords and next_word not in stopwords:
                        if rword in midboost:
                            pboost = pboost * 2.5
                        if next_word in midboost:
                            pboost = pboost * 2.5
                        if rword in keywords:
                            pboost = pboost * 4.0
                        if next_word in keywords:
                            pboost = pboost * 4.0
                        bigrams.append((rword, next_word, pboost))
                except BaseException:
                    pass

        for bigram in bigrams:
            word0 = bigram[0]
            word1 = bigram[1].replace('.', '')
            kpmatch = {"match_phrase": {"card": {'query': word0 + ' ' + word1, 'boost': bigram[2]}}}
            queryd['query']['bool']['should'].append(kpmatch)

        for kphrase in key_phrases:
            if phrase.find(kphrase) > -1:
                kpmatch = {"match_phrase": {"card": {'query': kphrase, 'boost': 12}}}
                queryd['query']['bool']['should'].append(kpmatch)

        for term in exclude_words:
            queryd['query']['bool']['must_not'].append({"match": {"card": term}})

        qq['query']["function_score"]['query'] = queryd['query']
        qq["size"] = max_results

        #import json
        #sys.stderr.write("query: {}\n".format(json.dumps(qq, indent=2)))

        similars = searchservice.search(index='card', body=qq)

        result = similars['hits']['hits']
        #sys.stdout.write("result: {}\n".format(json.dumps(result, indent=2)))

        return result

    def find_similar_cards(self, max_results=18, include_query_card=False):
        """ Returns Card objects, not PhysicalCard objects.

            BOOKMARK - need to make this work with pagination. Right now it hits the database for every card. :(
        """
        similars = self.find_similar_card_ids(max_results, include_query_card)
        result = []
        for sim in similars:
            try:
                card = PhysicalCard.objects.get(pk=int(sim['_id'])).get_latest_card()
                if card is not None:
                    # found issue with '1996 World Champion'. Has a PhysicalCard and BaseCard, but no Card.
                    try:
                        card.annotations
                    except AttributeError:
                        card.annotations = dict()
                    finally:
                        card.annotations['similarity_score'] = sim['_score']
                    result.append(card)
            except BaseException as e:
                logger.error(
                    "PhysicalCard.find_similiar_cards received exception when getting cards back from ElasticSearch and trying to find them in the database. PhysicalCard id {}.".format(
                        sim['_id']),
                    exc_info=True)
        return result

    def find_played_with_cards(self, format_list, max_results=18, type_filter=None):
        """ Returns a list of Card objects for cards that get played in the formats that are specified in the list. For instance, the
            format_list could be all of the formats that have the formatname 'Standard'.

            type_filter: a Type object that will be used to restrict the results to just that type.
        """
        format_ids = list()
        for f in format_list:
            if isinstance(f, Format):
                format_ids.append(f.id)
            else:
                format_ids.append(f)
        format_ids_str = ','.join(str(i) for i in format_ids)

        tfck = ''
        if type_filter:
            tfck = type_filter.id
        _cache_key = 'pc.fpwc_{}_{}_t{}'.format(self.id, format_ids_str, tfck)
        result = cache.get(_cache_key)
        if result is None:
            result = list()

            # first, let's get the deck count for this card, so we can calculate inclusion percentages
            tdc_query_str = u'''SELECT bc.physicalcard_id, SUM(dc.cardcount) AS tcc, COUNT(deck.id) AS tdc FROM deck JOIN deckcard AS dc ON deck.id = dc.deck_id JOIN basecard AS bc ON bc.physicalcard_id = dc.physicalcard_id AND bc.cardposition IN ('{}','{}','{}') JOIN deck AS jdeck ON deck.id = jdeck.id JOIN deckcard AS jdc ON jdc.deck_id = jdeck.id AND jdc.physicalcard_id = {} WHERE dc.physicalcard_id = {} AND deck.format_id IN ({}) GROUP BY bc.physicalcard_id ORDER BY tcc DESC'''.format(
                BaseCard.FRONT,
                BaseCard.LEFT,
                BaseCard.UP,
                str(self.id),
                str(self.id),
                format_ids_str)
            cursor = connection.cursor()
            cursor.execute(tdc_query_str)
            tdc_q_results = cursor.fetchall()

            if tdc_q_results:
                total_deck_count = tdc_q_results[0][2]

                type_join_clause = ''
                type_where_clause = ''
                if type_filter:
                    type_join_clause = ' JOIN cardtype AS ct ON ct.basecard_id = bc.id '
                    type_where_clause = ' AND ct.type_id = {} '.format(type_filter.id)

                query_str = u'''SELECT bc.physicalcard_id, SUM(dc.cardcount) AS tcc, COUNT(deck.id) AS tdc FROM deck JOIN deckcard AS dc ON deck.id = dc.deck_id JOIN basecard AS bc ON bc.physicalcard_id = dc.physicalcard_id AND bc.cardposition IN ('{}','{}','{}') JOIN deck AS jdeck ON deck.id = jdeck.id JOIN deckcard AS jdc ON jdc.deck_id = jdeck.id AND jdc.physicalcard_id = {} {} WHERE dc.physicalcard_id != {} AND deck.format_id IN ({}) {} GROUP BY bc.physicalcard_id ORDER BY tcc DESC LIMIT {}'''.format(
                    BaseCard.FRONT,
                    BaseCard.LEFT,
                    BaseCard.UP,
                    str(self.id),
                    type_join_clause,
                    str(self.id),
                    format_ids_str,
                    type_where_clause,
                    str(max_results))
                #sys.stderr.write("Q: {}\n".format(query_str))

                cursor = connection.cursor()
                cursor.execute(query_str)
                q_results = cursor.fetchall()
                for row in q_results:
                    #sys.stderr.write("pc_id and count is {}. deck count is {} and tdc is {}\n".format(row, row[2], total_deck_count))
                    ccc = PhysicalCard.objects.get(pk=row[0]).get_latest_card()
                    ccc.annotations = dict()
                    ccc.annotations['appearance_count'] = row[1]
                    ccc.annotations['appearance_percentage'] = 100 * float(row[2]) / float(total_deck_count)
                    result.append(ccc)
            else:
                # this card isn't played with anything else in this format
                pass
            cache.set(_cache_key, result, 60 * 60 * 72)  # 72 hours
            #sys.stderr.write("R: {}\n".format("\n".join(str(i) for i in result)))

        return result

    def legal_formats(self, start_date=timezone.now(), end_date=timezone.now()):
        """ Get the legal Formats for this card as of the given dates.

        Given a start_date (datetime) and end_date (datetime), returns a QuerySet of Format objects in which this card is/was legal.

        Arguments:
        start_date -- datetime.datetime object that represents the start of the format search.
        end_date -- datetime.datetime object that represents the last day of the format search.

        Returns: QuerySet of Format objects.
        """
        return Format.objects.filter(formatbasecard__basecard=self.get_face_basecard(),
                                     start_date__lte=start_date,
                                     end_date__gt=end_date)

    def latest_aggregate_cardprices(self):
        ckey = 'c_pc_laggcp-{}'.format(self.id)
        result = cache.get(ckey)
        if not result:
            oldest = timezone.now() - timedelta(days=14)
            latest_cp = CardPrice.objects.filter(card__basecard__physicalcard=self,
                                                 at_datetime__gt=oldest,
                                                 printing='normal')\
                .annotate(day=TruncDay('at_datetime')).values('day').order_by('-at_datetime').first()
            if latest_cp:
                result = CardPrice.objects.filter(card__basecard__physicalcard=self,
                                                  at_datetime__gte=latest_cp['day'])\
                    .aggregate(min=Min('price'), avg=Avg('price'), max=Max('price'), at_datetime=Min('at_datetime'))
                cache.set(ckey, result, settings.CARDS_SEARCH_CACHE_TIME)
        return result

    class Meta:
        managed = True
        db_table = 'physicalcard'
        verbose_name = 'Physical Card'
        verbose_name_plural = 'Physical Cards'

    def __unicode__(self):
        return '{} [PC:{}]'.format(self.get_card_name(), str(self.id))


class BaseCard(models.Model):
    FRONT = 'F'
    BACK = 'B'
    LEFT = 'L'
    RIGHT = 'R'
    UP = 'U'
    DOWN = 'D'
    #id = models.IntegerField(primary_key=True)
    physicalcard = models.ForeignKey(PhysicalCard, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, unique=True, blank=False)
    filing_name = models.CharField(max_length=128, blank=False)
    rules_text = models.CharField(max_length=1000, blank=True)
    mana_cost = models.CharField(max_length=60, null=False)
    cmc = models.IntegerField(null=False, default=0)
    power = models.CharField(max_length=4, null=True, blank=True)
    toughness = models.CharField(max_length=4, null=True, blank=True)
    loyalty = models.CharField(max_length=4, null=True, blank=True)
    ispermanent = models.BooleanField(null=False, default=False)
    created_at = models.DateTimeField(
        null=False,
        auto_now_add=True)
    updated_at = models.DateTimeField(
        null=False,
        auto_now=True)
    cardposition = models.CharField(max_length=1, null=False, default=FRONT)
    types = models.ManyToManyField(Type, through='CardType')
    supertypes = models.ManyToManyField(Supertype, through='CardSupertype')
    subtypes = models.ManyToManyField(Subtype, through='CardSubtype')
    colors = models.ManyToManyField(Color, through='CardColor')

    def __setattr__(self, attrname, val):
        super(BaseCard, self).__setattr__(attrname, val)

        if attrname == 'name':
            self.filing_name = self.make_filing_name(val)
            #sys.stderr.write('cards.models.BaseCard.set_name - "' + val + '" made filing name "' + self.filing_name + '"' + "\n")

        if attrname == 'mana_cost':
            super(BaseCard, self).__setattr__(attrname, str(val).lower())
            # REVISIT!
            self.cmc = 1

    def get_full_type_str(self):
        """ Returns a string of full type line that you would see on a card.

        Examples: "Legendary Creature - Human Wizard", "Enchantment", "Basic Land - Forest", "Tribal Instant - Goblin"
        """
        spt = u' '.join(str(v.supertype) for v in self.supertypes.all())
        tt = u' '.join(str(v.type) for v in self.types.all().order_by('sort_order'))
        t = u' '.join([spt.strip(), tt.strip()])
        a = t
        st = u' '.join(str(v.subtype) for v in self.subtypes.all())
        if len(st) > 0:
            a = u' - '.join([t, st])
        return a.strip()

    def get_rulings(self):
        return Ruling.objects.filter(basecard=self.id).order_by('ruling_date')

    def is_land(self):
        ct = CardType.objects.filter(type__type='Land', basecard=self).first()
        return ct is not None

    def make_filing_name(self, name):
        return filing_string(name)

    class Meta:
        managed = True
        db_table = 'basecard'
        verbose_name_plural = 'Base Cards'
        unique_together = ('physicalcard', 'cardposition',)

    def __unicode__(self):
        return self.name + \
            ' (physicalcard.id=' + str(self.physicalcard.id) + ')'

    def clean(self):
        # A name is required.
        if self.name is None or self.name == '':
            raise ValidationError('BaseCard must have a name.')
        # A filing_name is required.
        if self.filing_name is None or self.filing_name == '':
            raise ValidationError(
                'BaseCard must have a filing_name. It should be set through the name attribute.')

    def save(self):
        super(BaseCard, self).save()


class Ruling(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard, on_delete=models.CASCADE)
    ruling_text = models.TextField(null=False)
    ruling_date = models.DateField(null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Rulings'
        db_table = 'ruling'

    def __unicode__(self):
        return "Ruling " + str(self.id) + " for " + self.basecard.name


class ExpansionSet(models.Model):
    #id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=128)
    abbr = models.CharField(unique=False, max_length=10)
    releasedate = models.DateField(
        auto_now=False,
        auto_now_add=False,
        null=True)

    class Meta:
        managed = True
        db_table = 'expansionset'
        verbose_name_plural = 'Expansion Sets'

    def __unicode__(self):
        return self.name + " (" + self.abbr + ")"


class Mark(models.Model):
    #id = models.IntegerField(primary_key=True)
    mark = models.CharField(max_length=128)

    class Meta:
        managed = True
        db_table = 'mark'

    def __unicode__(self):
        return self.mark


class CardManager(models.Manager):

    def get_queryset(self, *args, **kwargs):
        # Not sure of the performance in here. Basically, I needed to
        # do a GROUP BY to get the max multiverseid and only display
        # that card. The first query here is getting the max
        # multiverseid for the given query. The second query then uses
        # that "mid_max" value to get back a list of all of the cards.
        card_listP = super(CardManager, self).get_queryset(*args, **kwargs)
        card_listP = card_listP.values('basecard__id').annotate(
            mid_max=Max('multiverseid'))
        card_list = super(CardManager, self).get_queryset()
        card_list = card_list.filter(
            multiverseid__in=[
                g['mid_max'] for g in card_listP]).order_by('basecard__filing_name')

        # Filer out the non-playing cards for now
        queryset = card_list.filter(
            basecard__physicalcard__layout__in=(
                'normal',
                'double-faced',
                'split',
                'flip',
                'aftermath',
                'leveler'))

        return queryset

    def get_latest_printing(self, *args, **kwargs):
        return self.get_queryset(*args, **kwargs)

    def in_cardrating_order(
            self,
            queryset,
            format_id=1,
            sort_order=1):
        #cursor = connection.cursor()
        #sql = 'SELECT bc.name, max(c.multiverseid), pc.id, cr.mu FROM physicalcard pc JOIN basecard bc ON pc.id = bc.physicalcard_id JOIN card c ON bc.id = c.basecard_id JOIN cardrating cr ON cr.physicalcard_id = pc.id WHERE cr.format_id = ' + str(format_id) + ' GROUP BY pc.id ORDER BY cr.mu'
        # cursor.execute(sql)
        #context['winners'] = cursor.fetchall()

        # Try 2
        #cr_qs = CardRating.objects.filter(format_id=format_id).order_by('mu')
        #result = {}
        #qs = self.get_queryset().filter(*args, **kwargs)
        # for card in qs:
        #	index = 0
        #	for cr in cr_qs:
        #		if cr.physicalcard.id == card.basecard.physicalcard.id:
        #			result[index] = card
        #		index = index + 1
        #list2 = [result[x] for x in result if x]
        # return reversed(list2)

        sql_ord = 'ASC'
        if sort_order <= 0:
            sql_ord = 'DESC'

        cards = self.raw(
            'SELECT c.id FROM physicalcard pc JOIN basecard bc ON pc.id = bc.physicalcard_id JOIN card c ON bc.id = c.basecard_id JOIN cardrating cr ON cr.physicalcard_id = pc.id WHERE cr.format_id = ' +
            str(format_id) +
            ' AND c.id IN (' +
            ','.join(str(card.id) for card in queryset) +
            ') GROUP BY pc.id HAVING max(c.multiverseid) ORDER BY cr.mu ' +
            sql_ord +
            ', bc.filing_name')
        return cards

    def search(self, *args, **kwargs):
        ''' Yea know, if there are NO terms, and just some sorting, let's make this easy on ourselves. '''
        has_search_predicates = False
        sortds = []
        all_args = []

        timer_start = time.time()
        for arg in args:
            if isinstance(arg, list):
                for subarg in arg:
                    all_args.append(subarg)
            else:
                all_args.append(arg)
        for arg in all_args:
            if isinstance(arg, SortDirective):
                sortds.append(arg)
            elif isinstance(arg, SearchPredicate):
                has_search_predicates = True
                continue
        if not has_search_predicates:
            # let's do it SIMPLE
            if not sortds:
                sd = SortDirective()
                sd.term = 'name'
                sortds.append(sd)
            positions = ','.join("'{}'".format(v) for v in [BaseCard.FRONT, BaseCard.LEFT, BaseCard.UP])
            layouts = ','.join(
                "'{}'".format(v) for v in [
                    PhysicalCard.TOKEN,
                    PhysicalCard.PLANE,
                    PhysicalCard.SCHEME,
                    PhysicalCard.PHENOMENON,
                    PhysicalCard.VANGUARD])
            cru_join = ''
            add_cardratings = False
            for sdir in sortds:
                if sdir.term == 'cardrating' and not add_cardratings:
                    add_cardratings = True
                    cru_join = ' LEFT JOIN cardrating AS crs ON crs.physicalcard_id = pc.id AND crs.format_id = {}'.format(
                        str(sdir.crs_format_id))

            sql_s = 'SELECT c.id FROM card AS c JOIN basecard AS bc ON c.basecard_id = bc.id JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id {} WHERE bc.cardposition IN ({}) AND pc.layout NOT IN ({}) GROUP BY bc.id HAVING MAX(c.multiverseid) '.format(
                cru_join,
                positions,
                layouts)

            sql_s = sql_s + ' ORDER BY '
            sql_s = sql_s + ', '.join(str(str(arg.sqlname()) + ' ' + arg.direction) for arg in sortds)

            cards = self.raw(sql_s)
            #logger.debug("CardManager.search() time: {}".format(time.time() - timer_start))
            #logger.debug("CardManager.search() SQL query: {}".format(cards))
            return cards
        else:
            # better use the more advanced search tools
            #logger.debug("L636: trying the hard way.")
            return self.search_harder(all_args, kwargs)

    def search_harder(self, *args, **kwargs):
        ''' Searches that contain a field SPECIFIC to a type (power and
            toughness for Creatures, loyalty for Planeswalkers), will
            LIMIT the search to just those cards. Thus, searching for
            cards with toughness != 1 WILL NOT return Swamp (since
            Swamp is not a creature).
        '''

        # use this to create unique table aliases as we add joins
        jcounter = 0

        pre_where_clause = ''
        # This version gets the one with the last multiverseid (ostinsibly, the latest one), but it is really, really slow. And take the HAVING clause out if you are using this one.
        #sql_s = '''SELECT c.id, c.basecard_id FROM physicalcard AS pc JOIN basecard AS bc ON pc.id = bc.physicalcard_id JOIN card AS c ON c.basecard_id = bc.id INNER JOIN (SELECT basecard_id, MAX(multiverseid) AS multiverseid FROM card GROUP BY basecard_id) AS cm ON cm.basecard_id = c.basecard_id AND cm.multiverseid = c.multiverseid LEFT JOIN formatbasecard AS f ON f.basecard_id = bc.id LEFT JOIN cardrating AS cr ON cr.physicalcard_id = pc.id '''
        sql_s = '''SELECT c.id, c.basecard_id FROM physicalcard AS pc JOIN basecard AS bc ON pc.id = bc.physicalcard_id JOIN card AS c ON c.basecard_id = bc.id LEFT JOIN cardrating AS cr ON cr.physicalcard_id = pc.id '''

        terms = []
        not_terms = []
        sortds = []
        specified_format = None

        safelocker = dict()
        safelocker['_counter'] = 0

        all_args = []

        for restriction in [PhysicalCard.TOKEN, PhysicalCard.PLANE, PhysicalCard.SCHEME, PhysicalCard.PHENOMENON, PhysicalCard.VANGUARD]:
            no_s = SearchPredicate()
            no_s.term = 'layout'
            no_s.negative = True
            no_s.value = restriction
            all_args.append(no_s)

        for arg in args:
            if isinstance(arg, list):
                for subarg in arg:
                    all_args.append(subarg)
            else:
                all_args.append(arg)

        add_formatbasecard_leftjoin = False
        # We must grab the format first
        for arg in all_args:
            if isinstance(arg, SortDirective):
                sortds.append(arg)
            elif isinstance(arg, SearchPredicate):
                if arg.term == 'format':
                    specified_format = arg.value
                    sql_p = ' f.format_id = %(sarg' + str(safelocker['_counter']) + ')s '
                    safelocker['sarg' + str(safelocker['_counter'])] = specified_format
                    safelocker['_counter'] = safelocker['_counter'] + 1
                    terms.append(sql_p)
                    add_formatbasecard_leftjoin = True
        if add_formatbasecard_leftjoin:
            sql_s = sql_s + ''' LEFT JOIN formatbasecard AS f ON f.basecard_id = bc.id '''

        if len(sortds) == 0:
            namesort = SortDirective()
            namesort.term = 'name'
            sortds.append(namesort)
        else:
            # go through the sort directives and handle card rating sorting, if needed
            for sd in sortds:
                # If we are sorting for card rating, we need to inject into the search criteria the format that we care about.
                if sd.term == 'cardrating':
                    pre_where_clause = ' LEFT JOIN cardrating AS crs ON crs.physicalcard_id = pc.id AND crs.format_id = ' + \
                        str(sd.crs_format_id)

        # Now we can process all of the other terms
        for arg in all_args:
            if isinstance(arg, SearchPredicate):
                if (arg.term == 'name'):
                    orc = []
                    for fieldname in ['bc.name', 'bc.filing_name']:
                        sql_p = fieldname
                        sql_p = sql_p + arg.text_sql_operator_and_value(safelocker)
                        orc.append(sql_p)
                    if arg.negative:
                        terms.append('(' + ' AND '.join(orc) + ')')
                    else:
                        terms.append('(' + ' OR '.join(orc) + ')')
                elif arg.term == 'rules':
                    sql_p = ' bc.rules_text '
                    sql_p = sql_p + arg.text_sql_operator_and_value(safelocker)
                    terms.append(sql_p)
                elif arg.term in ['ispermanent']:
                    sql_p = ' bc.ispermanent '
                    sql_p = sql_p + arg.numeric_sql_operator()
                    sql_p = sql_p + str(arg.value) + ' '
                    terms.append(sql_p)
                elif arg.term in ['toughness', 'power'] and '*' in str(arg.value):
                    # ONLY equality should be support here!! REVISIT
                    sql_p = ' bc.' + arg.term + ' '
                    sql_p = sql_p + arg.text_sql_operator_and_value(safelocker)
                    terms.append(sql_p)
                elif arg.term in ['cmc', 'toughness', 'power', 'loyalty']:
                    sql_p = ' bc.' + arg.term + ' '
                    sql_p = sql_p + arg.numeric_sql_operator()
                    sql_p = sql_p + str(arg.value) + ' '
                    terms.append(sql_p)
                elif arg.term == 'cardrating':
                    if specified_format is None:
                        raise self.FormatNotSpecifiedException()
                    # NOTE! A singular format must ALSO be provided!!
                    terms.append(' cr.format_id = ' + str(specified_format) + ' ')

                    sql_p = ' ROUND(cr.mu,5) '
                    sql_p = sql_p + arg.numeric_sql_operator()

                    # remember that the database stores it on a scale from 0 to 50, but it is presented to users as 0 to 1000
                    sql_p = sql_p + str(arg.value / 20.0) + ' '

                    terms.append(sql_p)
                elif arg.term == 'rarity':
                    sql_p = ' c.rarity '
                    sql_p = sql_p + arg.text_sql_operator_and_value(safelocker)
                    terms.append(sql_p)
                elif arg.term == 'color':
                    if arg.negative:
                        not_terms.append(arg)
                    else:
                        tab_alias = 'cc' + str(jcounter)
                        jcounter = jcounter + 1
                        pre_where_clause = pre_where_clause + ' JOIN cardcolor AS ' + \
                            tab_alias + ' ON bc.id = ' + tab_alias + '.basecard_id '
                        sql_p = ' ' + tab_alias + '.color_id ' + arg.text_sql_operator_and_value(safelocker)
                        terms.append(sql_p)
                elif arg.term == 'type':
                    if arg.negative:
                        not_terms.append(arg)
                    else:
                        tab_alias = 'ct' + str(jcounter)
                        jcounter = jcounter + 1
                        pre_where_clause = pre_where_clause + ' JOIN cardtype AS ' + \
                            tab_alias + ' ON bc.id = ' + tab_alias + '.basecard_id '
                        sql_p = ' ' + tab_alias + '.type_id = ' + str(arg.value)
                        terms.append(sql_p)
                elif arg.term == 'supertype':
                    if arg.negative:
                        not_terms.append(arg)
                    else:
                        tab_alias = 'cspt' + str(jcounter)
                        jcounter = jcounter + 1
                        pre_where_clause = pre_where_clause + ' JOIN cardsupertype AS ' + \
                            tab_alias + ' ON bc.id = ' + tab_alias + '.basecard_id '
                        sql_p = ' ' + tab_alias + '.supertype_id = ' + str(arg.value)
                        terms.append(sql_p)
                elif arg.term == 'subtype':
                    if arg.negative:
                        not_terms.append(arg)
                    else:
                        tab_alias = 'cst' + str(jcounter)
                        jcounter = jcounter + 1
                        pre_where_clause = pre_where_clause + ' JOIN cardsubtype AS ' + \
                            tab_alias + ' ON bc.id = ' + tab_alias + '.basecard_id '
                        sql_p = ' ' + tab_alias + '.subtype_id = ' + str(arg.value)
                        terms.append(sql_p)
                elif arg.term == 'layout':
                    sql_p = ' pc.layout ' + arg.text_sql_operator_and_value(safelocker)
                    terms.append(sql_p)

        sql_s = sql_s + pre_where_clause
        if len(terms) > 0:
            sql_s = sql_s + ' WHERE ' + ' AND '.join(terms)

        group_by_added = True
        sql_s = sql_s + ' GROUP BY pc.id '

        if len(not_terms) > 0:  # If we have to pull out some types and subtypes, we better do it now.
            # Let's execute the SQL we have (sql_s) but do it with cursor so that we do not instantiate any objects
            cursor = connection.cursor()
            cursor.execute(sql_s, params=safelocker)
            card_ids = cursor.fetchall()
            bc_ids = [row[1] for row in card_ids]
            if len(bc_ids) > 0:
                sql_s = 'SELECT c.id FROM physicalcard AS pc JOIN basecard AS bc ON pc.id = bc.physicalcard_id JOIN card AS c ON c.basecard_id = bc.id LEFT JOIN cardcolor AS cc ON cc.basecard_id = bc.id LEFT JOIN formatbasecard AS f ON f.basecard_id = bc.id LEFT JOIN cardrating AS cr ON cr.physicalcard_id = pc.id ' + \
                    pre_where_clause + ' WHERE bc.id IN (' + ','.join(str(i) for i in bc_ids) + ') '
                for arg in not_terms:
                    # Now that we have all of these ids, let's use them to filter out those types that we do not want.
                    try:
                        if arg.term == 'color':
                            sql_not = 'SELECT cc.basecard_id FROM cardcolor AS cc WHERE cc.color_id = \'' + \
                                str(arg.value) + '\' AND cc.basecard_id IN (' + ','.join(str(i) for i in bc_ids) + ')'
                            cursor.execute(sql_not)
                            not_basecard_ids = cursor.fetchall()
                            if len(not_basecard_ids) > 0:
                                sql_s = sql_s + ' AND bc.id NOT IN (' + ','.join(str(n[0]) for n in not_basecard_ids) + ') '
                        elif arg.term == 'type':
                            sql_not = 'SELECT ct.basecard_id FROM cardtype AS ct WHERE ct.type_id = ' + \
                                str(arg.value) + ' AND ct.basecard_id IN (' + ','.join(str(i) for i in bc_ids) + ')'
                            cursor.execute(sql_not)
                            not_basecard_ids = cursor.fetchall()
                            if len(not_basecard_ids) > 0:
                                sql_s = sql_s + ' AND bc.id NOT IN (' + ','.join(str(n[0]) for n in not_basecard_ids) + ') '
                        elif arg.term == 'subtype':
                            sql_not = 'SELECT cst.basecard_id FROM cardsubtype AS cst WHERE cst.subtype_id = ' + \
                                str(arg.value) + ' AND cst.basecard_id IN (' + ','.join(str(i) for i in bc_ids) + ')'
                            cursor.execute(sql_not)
                            not_basecard_ids = cursor.fetchall()
                            if len(not_basecard_ids) > 0:
                                sql_s = sql_s + ' AND bc.id NOT IN (' + ','.join(str(n[0]) for n in not_basecard_ids) + ') '
                        elif arg.term == 'supertype':
                            sql_not = 'SELECT cspt.basecard_id FROM cardsupertype AS cspt WHERE cspt.supertype_id = ' + \
                                str(arg.value) + ' AND cspt.basecard_id IN (' + ','.join(str(i) for i in bc_ids) + ')'
                            cursor.execute(sql_not)
                            not_basecard_ids = cursor.fetchall()
                            if len(not_basecard_ids) > 0:
                                sql_s = sql_s + ' AND bc.id NOT IN (' + ','.join(str(n[0]) for n in not_basecard_ids) + ') '
                    except ProgrammingError as pe:
                        logger.error("CardManager.search: SQL error in: {}".format(sql_not))
                        raise pe
                group_by_added = False

        if group_by_added:
            #sql_s = sql_s + ' , '
            pass
        else:
            sql_s = sql_s + ' GROUP BY ' + 'pc.id '
            #sql_s = sql_s + ' bc.id HAVING max(c.multiverseid) '
            #sql_s = sql_s + ' HAVING max(c.multiverseid) '

        sql_s = sql_s + ' ORDER BY '
        sql_s = sql_s + ', '.join(str(str(arg.sqlname()) + ' ' + arg.direction) for arg in sortds)

        #logger.debug("Card Search SQL: " + sql_s)
        #timer_start = time.time()
        cards = self.raw(sql_s, params=safelocker)
        #logger.debug("Card Search time: {}".format(time.time() - timer_start))
        #logger.debug("Card Search SQL query: {}".format(cards))

        return cards

    def get_simple_cards_list(self, card_names_to_skip=list()):
        result = list()
        #bcards = BaseCard.objects.filter(physicalcard_id__gt=7400, physicalcard_id__lt=7500).order_by('-filing_name')
        # These are cards that pretty much aren't going to be referenced - there are more false positives than actual hits.
        bcards = BaseCard.objects.exclude(name__in=card_names_to_skip).order_by('-filing_name')
        for basecard in bcards:
            card = basecard.physicalcard.get_latest_card()
            simple = {'name': basecard.name,
                      'cleanname': basecard.name,
                      'url_slug': card.url_slug(),
                      'name_len': len(basecard.name),
                      'multiverseid': card.multiverseid}
            result.append(simple)
            try:
                if basecard.name.index("'"):
                    simple = {'name': basecard.name.replace(u"'", u"’"),
                              'cleanname': basecard.name,
                              'url_slug': card.url_slug(),
                              'name_len': len(basecard.name),
                              'multiverseid': card.multiverseid}
                    result.append(simple)
            except ValueError:
                pass
            for sillydash in [u'–', u'—', u'‒', u'-']:
                try:
                    if basecard.name.index(sillydash):
                        simple = {'name': basecard.name.replace(sillydash, u'-'),
                                  'cleanname': basecard.name,
                                  'url_slug': card.url_slug(),
                                  'name_len': len(basecard.name),
                                  'multiverseid': card.multiverseid}
                        result.append(simple)
                except ValueError:
                    pass
                try:
                    if simple['name'].index('-'):
                        simple = {'name': basecard.name.replace('-', sillydash),
                                  'cleanname': basecard.name,
                                  'url_slug': card.url_slug(),
                                  'name_len': len(basecard.name),
                                  'multiverseid': card.multiverseid}
                        result.append(simple)
                except ValueError:
                    pass

        result = sorted(result, key=itemgetter('name_len'), reverse=True)
        return result

    class FormatNotSpecifiedException(Exception):
        pass


class SortDirective():
    ASC = 'ASC'
    DESC = 'DESC'
    term = None
    crs_format_id = None
    direction = ASC

    def sqlname(self):
        if self.term == 'name':
            return 'bc.filing_name'
        elif self.term == 'cmc':
            return 'bc.cmc'
        elif self.term == 'cardrating':
            return 'crs.mu'
        else:
            return self.term


class SearchPredicate():
    EQUALS = 0
    CONTAINS = 1
    LESS_THAN = 2
    GREATER_THAN = 3
    term = None
    negative = False
    operator = EQUALS
    value = None

    def numeric_sql_operator(self):
        res_s = ''
        if self.operator == self.LESS_THAN:
            if self.negative:
                res_s = res_s + ' >= '
            else:
                res_s = res_s + ' < '
        elif self.operator == self.GREATER_THAN:
            if self.negative:
                res_s = res_s + ' <= '
            else:
                res_s = res_s + ' > '
        else:  # assume equals
            if self.negative:
                res_s = res_s + ' <> '
            else:
                res_s = res_s + ' = '
        return res_s

    def text_sql_operator_and_value(self, param_bag):
        res_s = ''
        # assume equals
        if self.value is None:
            if self.negative:
                res_s = res_s + ' IS NOT NULL '
            else:
                res_s = res_s + ' IS NULL '
        else:
            ptoken = 'sarg' + str(param_bag['_counter'])
            if self.operator == self.CONTAINS:
                if self.negative:
                    res_s = res_s + ' NOT LIKE '
                else:
                    res_s = res_s + ' LIKE '
                #res_s = res_s + " '%%" + self.value + "%%' "
                param_bag[ptoken] = '%' + str(self.value) + '%'
            else:  # equality
                if self.negative:
                    res_s = res_s + ' != '
                else:
                    res_s = res_s + ' = '
                param_bag[ptoken] = str(self.value)
            res_s = res_s + ' %(' + ptoken + ')s '
            param_bag['_counter'] = param_bag['_counter'] + 1
        return res_s


class Card(models.Model):
    #id = models.IntegerField(primary_key=True)
    expansionset = models.ForeignKey('ExpansionSet', on_delete=models.CASCADE)
    basecard = models.ForeignKey(BaseCard, on_delete=models.CASCADE)
    rarity = models.ForeignKey('Rarity',
                               db_column='rarity',
                               blank=True,
                               null=True, on_delete=models.CASCADE)
    multiverseid = models.IntegerField(unique=False, blank=True, null=False)
    flavor_text = models.CharField(max_length=1000, blank=True, null=True)
    card_number = models.CharField(max_length=6, blank=True, null=True)
    mark = models.ForeignKey('Mark', blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(
        null=False,
        auto_now_add=True)
    updated_at = models.DateTimeField(
        null=False,
        auto_now=True)
    objects = models.Manager()
    playables = CardManager()

    def img_url(self):
        return '/img/' + str(self.multiverseid) + '.jpg'

    def mana_cost_html(self):
        return convertSymbolsToHTML(self.basecard.mana_cost)

    def rules_text_html(self):
        return convertSymbolsToHTML(self.basecard.rules_text)

    def flavor_text_html(self):
        return mark_safe(self.flavor_text)

    def url_slug(self):
        """ Turn & into spaces and spaces into slashes.
        """
        result = self.basecard.filing_name.replace('&', ' ').lower()
        return result.replace(' ', '-')

    def get_first_card(self):
        """ Returns the Front, Up, or Left Card for this card.

        The result could just be this current Card object, or it might be its pair. Will not return None.
        """
        result = self
        if self.basecard.cardposition not in (BaseCard.FRONT, BaseCard.UP, BaseCard.LEFT):
            result = Card.objects.filter(
                basecard__physicalcard=self.basecard.physicalcard,
                expansionset_id=self.expansionset.id,
                basecard__cardposition__in=[
                    BaseCard.FRONT,
                    BaseCard.LEFT,
                    BaseCard.UP]).first()
        return result

    def get_second_card(self):
        """ Returns the Back, Down, or Right Card for this card.

        The result could just be this current Card object, or it might be its pair. Will return None if there is no second Card.
        """
        result = None
        if self.basecard.cardposition in (BaseCard.FRONT, BaseCard.UP, BaseCard.LEFT):
            result = Card.objects.filter(
                basecard__physicalcard=self.basecard.physicalcard,
                expansionset_id=self.expansionset.id,
                basecard__cardposition__in=[
                    BaseCard.BACK,
                    BaseCard.RIGHT,
                    BaseCard.DOWN]).first()
        else:
            result = self
        return result

    def get_double_faced_card(self):
        """ Return the double-faced card for Innastrad (and similiar) cards.

        Returns None if there is no second side to the card. If it is double-faced, this will always return the other face (e.g., 'Delver
        of Secrerts' returns 'Insectile Aberation'; 'Insectile Aberation' returns 'Delver of Secrets').
        """
        result = None
        if self.basecard.physicalcard.layout != PhysicalCard.DOUBLE:
            return None
        face_needed = 'B'
        if self.basecard.cardposition == 'B':
            face_needed = 'F'
        qs = Card.objects.filter(
            basecard__cardposition=face_needed,
            basecard__physicalcard=self.basecard.physicalcard,
            expansionset_id=self.expansionset.id)
        try:
            result = qs[0]
        except KeyError:
            result = None
        return result

    def get_all_cards(self):
        """ Returns a tuple of all of the cards, in order.
        """
        first = self.get_first_card()
        second = self.get_second_card()
        return (first, second)

    def get_original_version(self):
        """ Returns the Card of this card with the lowest Multiverseid.
        """
        return Card.objects.filter(basecard=self.basecard).order_by('multiverseid').first()

    def get_all_versions(self):
        """ Returns a QuerySet of Cards that are first cards (Up, Front, Left) that share this card's PhysicalCard.
        """
        return Card.objects.filter(
            basecard__physicalcard=self.basecard.physicalcard,
            basecard__cardposition__in=[
                BaseCard.FRONT,
                BaseCard.LEFT,
                BaseCard.UP]).order_by('multiverseid')

    def get_recent_lowest_cardprice(self):
        history = timezone.now() - timedelta(days=14)
        cp = CardPrice.objects.filter(card=self, at_datetime__gt=history).order_by('price', '-at_datetime').first()
        return cp

    class Meta:
        managed = True
        db_table = 'card'
        unique_together = ('expansionset', 'card_number', 'multiverseid')

    def __unicode__(self):
        return self.basecard.name + \
            "(" + self.expansionset.abbr + ") [" + str(self.multiverseid) + "]"


class CardColor(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard, on_delete=models.CASCADE)
    color = models.ForeignKey('Color', on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'cardcolor'
        unique_together = ('basecard', 'color',)


class CardSupertype(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard, on_delete=models.CASCADE)
    supertype = models.ForeignKey('Supertype', on_delete=models.CASCADE)
    position = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cardsupertype'
        unique_together = ('basecard', 'position',)


class CardSubtype(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard, on_delete=models.CASCADE)
    subtype = models.ForeignKey('Subtype', on_delete=models.CASCADE)
    position = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cardsubtype'
        unique_together = ('basecard', 'position',)


class CardType(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard, on_delete=models.CASCADE)
    type = models.ForeignKey('Type', on_delete=models.CASCADE)
    position = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cardtype'
        unique_together = ('basecard', 'position',)

    def __unicode__(self):
        return str(
            self.id) + " [Card: " + str(
            self.basecard.id) + " (" + self.basecard.name + "), Type: " + str(
            self.type.id) + " (" + self.type.type + "), Position: " + str(
                self.position) + "]"


class FormatManager(models.Manager):

    def current_legal_formats(self, card):
        """ Look up all of the formats where this card is currently legal.
        """
        # formats = FormatBasecard.objects.filter(basecard__id=card.basecard.id,
        #                                        format__start_date__lte=datetime.today(),
        #                                        format__end_date__gte=datetime.today())
        formats = Format.objects.filter(formatbasecard__basecard_id=card.basecard.id,
                                        start_date__lte=timezone.now(),
                                        end_date__gt=timezone.now())
        return formats

    def copy_format(self, format, new_name_of_format=None):
        new_format = Format()
        new_format.formatname = format.formatname
        if new_name_of_format:
            new_format.format = new_name_of_format
        else:
            new_format.format = u'Copy of {}'.format(format.format)
        new_format.abbr = format.abbr
        new_format.min_cards_main = format.min_cards_main
        new_format.max_cards_main = format.max_cards_main
        new_format.min_cards_side = format.min_cards_side
        new_format.max_cards_side = format.max_cards_side
        new_format.max_nonbl_card_count = format.max_nonbl_card_count
        new_format.uses_command_zone = format.uses_command_zone
        new_format.validator = format.validator
        new_format.start_date = format.start_date
        new_format.end_date = format.end_date
        new_format.save()
        # just want to make sure that we aren't keeping any old references and creating hard-to-find bugs
        result = Format.objects.get(pk=new_format.id)

        for expset in format.expansionsets.all():
            fes = FormatExpansionSet()
            fes.format = result
            fes.expansionset = expset
            fes.save()
        for bannedcard in format.bannedcards.all():
            banned = FormatBannedCard()
            banned.format = result
            banned.physicalcard = bannedcard
            banned.save()

        return result


def ddvalstart(value):
    # REVISIT  - THIS HAS NOT BEEN IMPLEMENTED
    sys.stderr.write("ddvalstart val is " + str(value) + "\n")
    if value is None:
        return
    if value == date(year=2015, month=3, day=5):
        raise ValidationError(
            _('%(value) is not an even number'),
            params={'value': str(value)},
        )


class Format(models.Model):
    id = models.AutoField(primary_key=True)
    formatname = models.CharField(max_length=60, null=False)
    format = models.CharField(max_length=60, unique=True, null=False)
    abbr = models.CharField(max_length=6, unique=False, null=True)
    min_cards_main = models.IntegerField(null=False, default=60)
    max_cards_main = models.IntegerField(null=False, default=60)
    min_cards_side = models.IntegerField(null=False, default=0)
    max_cards_side = models.IntegerField(null=False, default=15)
    max_nonbl_card_count = models.IntegerField(null=False, default=4)
    uses_command_zone = models.BooleanField(default=False)
    validator = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        null=True,
        validators=[ddvalstart])
    end_date = models.DateField(auto_now=False, auto_now_add=False, null=True)

    expansionsets = models.ManyToManyField(ExpansionSet, through='FormatExpansionSet')
    bannedcards = models.ManyToManyField(PhysicalCard, through='FormatBannedCard')

    objects = models.Manager()
    cards = FormatManager()

    def populate_format_cards(self):
        """ Remove all FormatBasecards for this format and then add new ones based on recalcuating.

        When you create a new format, you need to populate it with cards. You do that by associating Expansion Sets with a Format, adding
        some Banned Cards, and then running this command. This command will clear out all of the FormatBaseCards, then add all cards from
        the named Expansion Sets, except for the Banned Cards.
        """

        # start from scratch. Delete all of the old cards.
        FormatBasecard.objects.filter(format=self).delete()

        # Now, go through all of the expansion sets associated with this
        # format, and add all cards.
        for expset in self.formatexpansionset_set.all():
            for card in Card.objects.filter(expansionset=expset.expansionset).all():
                fbc, created = FormatBasecard.objects.get_or_create(format=self, basecard=card.basecard)

        # Now, delete all of the banned cards associated with this format.
        for banned in self.formatbannedcard_set.all():
            for basecard in BaseCard.objects.filter(physicalcard=banned.physicalcard).all():
                FormatBasecard.objects.filter(format=self, basecard=basecard).delete()

        # REVISIT - looking over the banned list before adding to the
        # database may actually be more performant, but since this is
        # a not-so-often admin function, I am not worried about it.
        return

    def card_count(self):
        return FormatBasecard.objects.filter(format=self).count()

    class Meta:
        verbose_name_plural = 'Formats'
        db_table = 'format'

    def __unicode__(self):
        return str(
            self.id) + " [Format: " + str(self.formatname) + " (" + self.format + ")]"


class FormatExpansionSet(models.Model):
    format = models.ForeignKey(Format, on_delete=models.CASCADE)
    expansionset = models.ForeignKey(ExpansionSet, on_delete=models.CASCADE)

    class Meta:
        #auto_created = True
        #managed = True
        verbose_name_plural = 'Format Expansion Sets'
        db_table = 'formatexpansionset'

    def __unicode__(self):
        return "Format: " + str(self.format.format) + " - " + self.expansionset.name + " (" + str(self.expansionset.id) + ")"


class FormatBannedCard(models.Model):
    format = models.ForeignKey(Format, on_delete=models.CASCADE)
    physicalcard = models.ForeignKey(PhysicalCard, on_delete=models.CASCADE)

    class Meta:
        #managed = True
        verbose_name_plural = 'Format Banned Cards'
        db_table = 'formatbannedcard'

    def __unicode__(self):
        return "Format: " + str(self.format.format) + " - " + self.physicalcard.get_card_name() + " (" + str(self.physicalcard.id) + ")"


class FormatBasecard(models.Model):
    format = models.ForeignKey(Format, on_delete=models.CASCADE)
    basecard = models.ForeignKey(BaseCard, on_delete=models.CASCADE)

    def won_battles(self):
        """ Get all Battles won for this card in this format.

        This is a handy shortcut for templates looking to get won battles from the FormatBasecard.

        Returns: QuerySet of Battles
        """
        return self.basecard.physicalcard.won_battles.filter(format=self.format)

    def lost_battles(self):
        """ Get all Battles lost for this card in this format.

        This is a handy shortcut for templates looking to get lost battles from the FormatBasecard.

        Returns: QuerySet of Battles
        """
        return self.basecard.physicalcard.lost_battles.filter(format=self.format)

    def cards_played_with_all(self, lookback_timeframe=timezone.now() - timedelta(days=2 * 365)):
        return self.cards_played_with(lookback_timeframe, 1024)

    def cards_played_with_lands(self, lookback_timeframe=timezone.now() - timedelta(days=2 * 365), max_results=36):
        type_filter = Type.objects.filter(type__iexact='Land').first()
        return self.cards_played_with(lookback_timeframe, max_results=max_results, type_filter=type_filter)

    def cards_played_with_creatures(self, lookback_timeframe=timezone.now() - timedelta(days=2 * 365), max_results=36):
        type_filter = Type.objects.filter(type__iexact='Creature').first()
        return self.cards_played_with(lookback_timeframe, max_results=max_results, type_filter=type_filter)

    def cards_played_with_planeswalkers(self, lookback_timeframe=timezone.now() - timedelta(days=2 * 365), max_results=36):
        type_filter = Type.objects.filter(type__iexact='Planeswalker').first()
        return self.cards_played_with(lookback_timeframe, max_results=max_results, type_filter=type_filter)

    def cards_played_with_enchantments(self, lookback_timeframe=timezone.now() - timedelta(days=2 * 365), max_results=36):
        type_filter = Type.objects.filter(type__iexact='Enchantment').first()
        return self.cards_played_with(lookback_timeframe, max_results=max_results, type_filter=type_filter)

    def cards_played_with_instants(self, lookback_timeframe=timezone.now() - timedelta(days=2 * 365), max_results=36):
        type_filter = Type.objects.filter(type__iexact='Instant').first()
        return self.cards_played_with(lookback_timeframe, max_results=max_results, type_filter=type_filter)

    def cards_played_with_sorceries(self, lookback_timeframe=timezone.now() - timedelta(days=2 * 365), max_results=36):
        type_filter = Type.objects.filter(type__iexact='Sorcery').first()
        return self.cards_played_with(lookback_timeframe, max_results=max_results, type_filter=type_filter)

    def cards_played_with_artifacts(self, lookback_timeframe=timezone.now() - timedelta(days=2 * 365), max_results=36):
        type_filter = Type.objects.filter(type__iexact='Artifact').first()
        return self.cards_played_with(lookback_timeframe, max_results=max_results, type_filter=type_filter)

    def cards_played_with(self, lookback_timeframe=timezone.now() - timedelta(days=2 * 365), max_results=18, type_filter=None):
        """ Gets Cards that this BaseCard has played with in this Format over some period of time.

        Arguments:
        lookback_timeframe -- the start time from which to look for Formats that have the same formatname as self.format. Defaults to 2
                              years ago from today.
        max_results -- maximum number of results to return. Defaults to 18. (The underlying query is not a native ORM QuerySet, so typical
                       QuerySet result set limiting doesn't work.)

        Returns: list of Card objects that self.basecard is played with in self.format.formatname since lookback_timeframe.
        """
        formats = Format.objects.filter(formatname=self.format.formatname,
                                        start_date__gte=lookback_timeframe)
        return self.basecard.physicalcard.find_played_with_cards(formats, max_results=max_results, type_filter=type_filter)

    class Meta:
        verbose_name_plural = 'Format Base Cards'
        unique_together = ('format', 'basecard',)
        db_table = 'formatbasecard'

    def __unicode__(self):
        return "[Format: " + str(self.format.format) + " - " + \
            self.basecard.name + " (" + str(self.basecard.id) + ")]"


class Battle(models.Model):
    #id = models.IntegerField(primary_key=True)
    format = models.ForeignKey('Format', on_delete=models.CASCADE)
    winner_pcard = models.ForeignKey('PhysicalCard', related_name='won_battles', on_delete=models.CASCADE)
    loser_pcard = models.ForeignKey('PhysicalCard', related_name='lost_battles', on_delete=models.CASCADE)
    battle_date = models.DateTimeField(
        auto_now_add=True,
        null=False)
    session_key = models.CharField(null=False, max_length=40)

    class Meta:
        verbose_name_plural = 'Battles'
        db_table = 'battle'
        unique_together = (
            'format',
            'winner_pcard',
            'loser_pcard',
            'session_key')

    def __unicode__(self):
        return "[Battle " + str(self.id) + ": " + str(self.winner_pcard.id) + \
            " > " + str(self.loser_pcard.id) + " in " + self.format.format + "]"


class CardRating(models.Model):
    id = models.AutoField(primary_key=True)
    physicalcard = models.ForeignKey('PhysicalCard', on_delete=models.CASCADE)
    mu = models.FloatField(default=25.0, null=False)
    sigma = models.FloatField(default=25.0 / 3.0, null=False)
    format = models.ForeignKey('Format', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(
        auto_now=True,
        null=False)

    def cardninjaRating(self):
        return self.mu * 20.0

    def confidence(self):
        return 100.0 * ((25.0 / 3.0) - self.sigma) / (25.0 / 3.0)

    class Meta:
        verbose_name_plural = 'Card Ratings'
        unique_together = ('physicalcard', 'format')
        db_table = 'cardrating'

    def __unicode__(self):
        return "[CardRating " + str(self.id) + ": " + str(self.physicalcard.id) + " mu=" + str(self.mu) + " sigma=" + str(
            self.sigma) + " for format \"" + str(self.format.format) + "\"]"


class CardBattleStats():

    """ Transient/volatile class for battle statistics for a PhysicalCard and a Format.
    """

    def __init__(self, physicalcard, format):
        self.physicalcard = physicalcard
        self.format = format

    def __unicode__(self):
        try:
            return u'[CardBattleStats for "{}" in "{}"]'.format(self.physicalcard.get_card_name(), self.format.format)
        except BaseException:
            return u'[CardBattleStats for [{}] in [{}]]'.format(self.physicalcard.id, self.format.id)

    def won_battles(self):
        """ Annotated dictionary of PhysicalCard.ids and the number of times that PhysicalCard has been beaten by self.physicalcard in
        self.format.

        Returns: annotated QuerySet of cards this self.physicalcard has beaten in self.format.
        """
        result = Battle.objects.filter(winner_pcard=self.physicalcard, format=self.format).values(
            'loser_pcard_id').annotate(num_wins=Count('loser_pcard_id')).order_by('-num_wins')
        return result

    def lost_battles(self):
        """ Annotated dictionary of PhysicalCard.ids and the number of times that PhysicalCard has beaten self.physicalcard in
        self.format.

        Returns: annotated QuerySet of cards this self.physicalcard has lost to in self.format.
        """
        result = Battle.objects.filter(loser_pcard=self.physicalcard, format=self.format).values(
            'winner_pcard_id').annotate(num_losses=Count('winner_pcard_id')).order_by('-num_losses')
        return result

    def win_count(self):
        """ Number of times self.physicalcard has won in self.format.
        """
        return Battle.objects.filter(winner_pcard=self.physicalcard, format=self.format).count()

    def loss_count(self):
        """ Number of times self.physicalcard has lost in self.format.
        """
        return Battle.objects.filter(loser_pcard=self.physicalcard, format=self.format).count()

    def battle_count(self):
        """ Number of times self.physicalcard has battled in self.format.
        """
        return self.win_count() + self.loss_count()

    def win_percentage(self, return_on_div_by_zero='n/a'):
        """ Percentage of times self.physicalcard has won battles in self.format.

        Arguments:
        return_on_div_by_zero -- value to return if there is a division by zero error. Defaults to the string 'n/a'.

        Returns: float that is a percentage number (e.g., 10.5 is returned for 10.5%, not 0.105). If self.physicalcard has never battled
                 in self.format, then return_on_div_by_zero is returned.
        """
        if self.battle_count() > 0:
            return 100.0 * float(self.win_count()) / float(self.battle_count())
        else:
            return return_on_div_by_zero

    def loss_percentage(self, return_on_div_by_zero='n/a'):
        """ Percentage of times self.physicalcard has lost battles in self.format.

        Arguments:
        return_on_div_by_zero -- value to return if there is a division by zero error. Defaults to the string 'n/a'.

        Returns: float that is a percentage number (e.g., 10.5 is returned for 10.5%, not 0.105). If self.physicalcard has never battled
                 in self.format, then return_on_div_by_zero is returned.
        """
        if self.battle_count() > 0:
            return 100.0 * float(self.loss_count()) / float(self.battle_count())
        else:
            return return_on_div_by_zero


class CardKeyword(models.Model):
    #id = models.IntegerField(primary_key=True)
    physicalcard = models.ForeignKey(PhysicalCard, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=60, null=False)
    kwscore = models.FloatField(null=False)

    class Meta:
        managed = True
        db_table = 'cardkeyword'


class SimilarPhysicalCard(models.Model):
    #id = models.IntegerField(primary_key=True)
    score = models.FloatField(null=False)
    physicalcard = models.ForeignKey(PhysicalCard, related_name='physicalcard', on_delete=models.CASCADE)
    sim_physicalcard = models.ForeignKey(PhysicalCard, related_name='simphysicalcard', on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'similarphysicalcard'


class Association(models.Model):
    #id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=250, null=False)
    classification = models.CharField(max_length=60, null=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(
        null=False,
        auto_now_add=True)
    updated_at = models.DateTimeField(
        null=False,
        auto_now=True)
    associationcards = models.ManyToManyField(PhysicalCard, through='AssociationCard')

    class Meta:
        managed = True
        db_table = 'association'
        verbose_name = 'Association'
        verbose_name_plural = 'Associations'

    def __unicode__(self):
        return str(self.name) + ' [' + str(self.id) + ']'


class AssociationCard(models.Model):
    #id = models.IntegerField(primary_key=True)
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    physicalcard = models.ForeignKey(PhysicalCard, related_name='assocphysicalcard', on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'associationcard'

    def __unicode__(self):
        return str(self.physicalcard) + ' => ' + str(self.association) + ' [' + str(self.id) + ']'


class CardPrice(models.Model):

    """ Price of a card.
    """

    # BOOKMARK - make a Manager for this that can return interpolated results
    # via on overriden QuerySet class. That would be cool. Like
    # InterpolatedQuerySet or something like that.

    #id = models.IntegerField(primary_key=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    at_datetime = models.DateTimeField(
        null=False,
        auto_now=True)
    price = models.FloatField(default=0.0, null=False)
    price_discounted = models.BooleanField(null=False, default=False)

    # "normal", "foil", etc...
    printing = models.CharField(max_length=25)

    interpolated = False

    class Meta:
        managed = True
        db_table = 'cardprice'

    def __unicode__(self):
        return u'{}-{} ({}) [{}]: ${}'.format(self.card.multiverseid, self.card.basecard.physicalcard.get_card_name(),
                                              self.printing, self.at_datetime, self.price)
