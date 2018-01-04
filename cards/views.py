# -*- coding: utf-8 -*-

from django.utils.safestring import mark_safe
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.db.models import Max, Min, Count
from django.shortcuts import redirect
from django.http import Http404
from django.db import connection
from django.db import IntegrityError
import collections
from django.core.urlresolvers import reverse
from haystack.query import SearchQuerySet
from django.conf import settings

import random
import operator
import os.path
import sys

from cards.models import Card, CardManager, SearchPredicate, SortDirective, BaseCard
from cards.models import Mark
from cards.models import PhysicalCard
from cards.models import Type
from cards.models import Supertype
from cards.models import Subtype
from cards.models import Format
from cards.models import FormatBasecard
from cards.models import Ruling
from cards.models import Rarity
from cards.models import Battle
from cards.models import BattleTest
from cards.models import CardRating
from cards.models import Association
from cards.models import AssociationCard

from decks.models import FormatCardStat, FormatStat

from django.db.models import Q
from datetime import datetime, timedelta
import time

from django.core.cache import cache

# import the logging library
import logging

from trueskill import TrueSkill, Rating, quality_1vs1, rate_1vs1
from functools import reduce

color_slang = [['azorius', ['white', 'blue']],
               ['orzhov', ['white', 'black']],
               ['boros', ['white', 'red']],
               ['selesnya', ['white', 'green']],
               ['dimir', ['blue', 'black']],
               ['izzet', ['blue', 'red']],
               ['simic', ['blue', 'green']],
               ['rakdos', ['black', 'red']],
               ['golgari', ['black', 'green']],
               ['gruul', ['red', 'green']],
               ['esper', ['white', 'blue', 'black']],
               ['jeskai', ['white', 'blue', 'red']],
               ['bant', ['white', 'blue', 'green']],
               ['grixis', ['blue', 'black', 'red']],
               ['sultai', ['blue', 'black', 'green']],
               ['jund', ['black', 'red', 'green']],
               ['mardu', ['black', 'red', 'white']],
               ['naya', ['red', 'green', 'white']],
               ['temur', ['red', 'green', 'blue']],
               ['abzan', ['green', 'white', 'black']]]

#
# The index view simple shows a search page. The page may be
# interactive, but the index view has no specific interactions
#
# From the index template's search interface, the user may
# "search", which uses the search method. This method removes all search
#  query terms from the sessions, and then sets the new ones based on
# what you entered. With search terms set in the session, you are then
# sent on to the list.
#
# The "list" view method performs the query given the search terms in
# the session, and then pushes that list out to the template to be
# displayed. This view also handles pagination.
#
# If you like what see on the list, then you can view the "details" of
# the card.
#


def index(request):
    context = {}
    try:
        request.session['query_pred_array'] is None
    except KeyError:
        request.session['query_pred_array'] = []

    context['predicates'] = request.session.get('query_pred_array')
    context['predicates_js'] = json.dumps(
        request.session.get('query_pred_array'))
    context['types'] = [tt.type for tt in Type.objects.all()]
    context['supertypes'] = [st.supertype for st in Supertype.objects.all()]
    context['subtypes'] = [st.subtype for st in Subtype.objects.all()]
    context['rarities'] = [{'id': rr.id, 'rarity': rr.rarity}
                           for rr in Rarity.objects.all().order_by('sortorder')]
    context['formats'] = [
        {
            'format': f.format,
            'formatname': f.formatname,
            'start_date': f.start_date} for f in Format.objects.all().order_by('format')]
    context['current_formats'] = Format.objects.filter(start_date__lte=datetime.today(),
                                                       end_date__gte=datetime.today()).order_by('format')
    com_searches = {'All cards': '_search'}
    for color in ['white', 'blue', 'black', 'red', 'green', 'colorless', 'five-color']:
        com_searches['{} Commanders'.format(color.capitalize())] = '/cards/search/{}-commanders/'.format(color)
        com_searches['{} Planeswalkers'.format(color.capitalize())] = '/cards/search/{}-planeswalkers/'.format(color)
    for guild, gcolors in color_slang:
        com_searches['{} Commanders'.format(guild.capitalize())] = '/cards/search/{}-commanders/'.format('-'.join(gcolors))
        com_searches['{} Planeswalkers'.format(guild.capitalize())] = '/cards/search/{}-planeswalkers/'.format('-'.join(gcolors))

    context['common_searches'] = com_searches
    return render(request, 'cards/index.html', context)


def predefsearch(request, terms=None):
    query_pred_array = []
    page_title_words = []
    uses_slang = False
    for guild, gcolors in color_slang:
        if guild in terms:
            for gc in gcolors:
                terms = '{}-{}'.format(terms, gc)
            uses_slang = True
            page_title_words.append(guild.capitalize())
    if 'planeswalker' in terms:
        query_pred_array.append({"field": "type", "op": "and", "value": "Planeswalker", "hint": "typeandPlaneswalker"})
        request.session['sort_order'] = 'name'
    elif 'edh' in terms or 'commander' in terms:
        query_pred_array.append({"field": "supertype", "op": "and", "value": "Legendary", "hint": "supertypeandLegendary"})
        query_pred_array.append({"field": "type", "op": "and", "value": "Creature", "hint": "typeandCreature"})
        if 'tiny' in terms:
            cformat = Format.objects.filter(formatname='TinyLeaders',
                                            start_date__lte=datetime.today(),
                                            end_date__gte=datetime.today()).first()
            query_pred_array.append({"field": "format", "op": "and", "value": cformat.format, "hint": "format"})
            request.session['sort_order'] = 'rating-{}'.format(cformat.format)
        else:
            cformat = Format.objects.filter(formatname='Commander',
                                            start_date__lte=datetime.today(),
                                            end_date__gte=datetime.today()).first()
            query_pred_array.append({"field": "format", "op": "and", "value": cformat.format, "hint": "format"})
            request.session['sort_order'] = 'rating-{}'.format(cformat.format)
    colors = [['white', 'w'],
              ['blue', 'u'],
              ['black', 'b'],
              ['red', 'r'],
              ['green', 'g']]
    if 'five' in terms:
        for color, cid in colors:
            query_pred_array.append({"field": "color", "op": "and", "value": cid, "hint": "colorand{}".format(cid)})
        if not uses_slang:
            page_title_words.append('Five-color')
    elif 'colorless' in terms:
        for color, cid in colors:
            query_pred_array.append({"field": "color", "op": "not", "value": cid, "hint": "colornot{}".format(cid)})
            query_pred_array.append({"field": "rules", "op": "not", "value": "{" + cid + "}", "hint": "rulesnot" + cid})
        if not uses_slang:
            page_title_words.append('Colorless')
    else:
        for color, cid in colors:
            if color in terms:
                query_pred_array.append({"field": "color", "op": "and", "value": cid, "hint": "colorand{}".format(cid)})
                if not uses_slang:
                    page_title_words.append(color.capitalize())
            else:
                query_pred_array.append({"field": "color", "op": "not", "value": cid, "hint": "colornot{}".format(cid)})

    if request.GET.get('sort', False):
        sort_order = request.GET.get('sort', 'name')
        request.session['sort_order'] = sort_order
    request.session['query_pred_array'] = query_pred_array
    #sys.stderr.write("L180: " + json.dumps(request.session['query_pred_array']) + "\n")
    if 'planeswalker' in terms:
        page_title_words.append('Planeswalkers')
    elif 'edh' in terms or 'commander' in terms:
        page_title_words.append('Commanders')

    return cardlist(request, page_title=' '.join(page_title_words))


def search(request):
    logger = logging.getLogger(__name__)
    if request.session.get('query_pred_array', False):
        request.session["curpage"] = 1
        del request.session['query_pred_array']
    if request.GET.get('query', False):
        q_array = json.loads(request.GET.get('query', ''))
        logger.error(q_array)
        request.session['query_pred_array'] = q_array
    if request.GET.get('sort', False):
        sort_order = request.GET.get('sort', 'name')
        logger.error(sort_order)
        request.session['sort_order'] = sort_order

    return redirect('cards:list')


def autocomplete(request):
    logger = logging.getLogger(__name__)
    sqs = SearchQuerySet().autocomplete(name_auto=request.GET.get('q', ''))[:15]
    #suggestions = [result.name for result in sqs]
    suggestions = []
    for result in sqs:
        cardname = result.name
        #sys.stderr.write("L211 cardname is " + str(cardname) + " and pk is " + str(result.pk) + "\n")
        if cardname is not None and len(cardname) > 0:
            # sys.stderr.write("L213\n")
            cn_bc = BaseCard.objects.filter(physicalcard__id=result.pk).first()
            #sys.stderr.write("L215 " + str(cn_bc) + "\n")
            result = {'name': cardname}
            if cn_bc is not None:
                the_card = cn_bc.physicalcard.get_latest_card()
                #sys.stderr.write("L218 the_card " + str(the_card) + "\n")
                result['url'] = reverse('cards:detail', kwargs={'multiverseid': str(the_card.multiverseid), 'slug': the_card.url_slug()})
                suggestions.append(result)
    # Make sure you return a JSON object, not a bare list.
    # Otherwise, you could be vulnerable to an XSS attack.
    the_data = json.dumps(suggestions)

    if 'callback' in request.GET or 'callback' in request.POST:
        # a jsonp response!
        callback_request = None
        if 'callback' in request.GET:
            callback_request = request.GET['callback']
        elif 'callback' in request.POST:
            callback_request = request.POST['callback']
        the_data = '%s(%s);' % (callback_request, the_data)
        return HttpResponse(the_data, "text/javascript")
    else:
        return HttpResponse(the_data, content_type='application/json')


def cardlist(request, query_pred_array=None, page_title='Search Results'):
    # Get an instance of a logger
    logger = logging.getLogger(__name__)
    # logger.error(request)
    start_time = time.time()
    logger.debug("L247 start")
    # Let's get the array of predicates from the session
    if query_pred_array is None:
        query_pred_array = []
        if request.session.get('query_pred_array', False):
            query_pred_array = request.session.get('query_pred_array')

    spreds = []
    latest_time = time.time()
    logger.debug("L258 {}".format(str(latest_time - start_time)))
    for pred in query_pred_array:
        # check to see if it is a sort order or a search predicate
        if 'field' not in pred:
            query_pred_array.remove(pred)
            break

        spred = SearchPredicate()
        spred.term = pred['field']
        spred.value = pred['value']
        spred.operator = spred.EQUALS
        spred.negative = pred['op'] == 'not'
        if pred['field'] == 'cardname':
            spred.operator = spred.CONTAINS
            spred.term = 'name'
        elif pred['field'] == 'rules':
            spred.operator = spred.CONTAINS
        elif pred['field'] == 'color':
            pass
        elif pred['field'] == 'rarity':
            # REVISIT - need to handle 'or'
            pass
        elif pred['field'] == 'cmc' or pred['field'] == 'power' or pred['field'] == 'toughness':
            spred.negative = False
            # If it isn't an int, then skip it.
            try:
                pred['value'] = int(pred['value'])
            except ValueError:
                # we should remove this predicate. it is bogus
                query_pred_array.remove(pred)
                break
            if pred['op'] == 'lt':
                spred.operator = spred.LESS_THAN
            if pred['op'] == 'gt':
                spred.operator = spred.GREATER_THAN
            if pred['op'] == 'ne':
                spred.negative = True
        elif pred['field'] == 'type':
            type_lookup = Type.objects.filter(type__iexact=pred['value']).first()
            if type_lookup is None:
                spred.value = -1
            else:
                spred.value = type_lookup.id
        elif pred['field'] == 'supertype':
            supertype_lookup = Supertype.objects.filter(supertype__iexact=pred['value']).first()
            if supertype_lookup is None:
                spred.value = -1
            else:
                spred.value = supertype_lookup.id
        elif pred['field'] == 'subtype':
            subtype_lookup = Subtype.objects.filter(subtype__iexact=pred['value']).first()
            if subtype_lookup is None:
                spred.value = -1
            else:
                spred.value = subtype_lookup.id
        elif pred['field'] == 'ispermanent':
            spred.term = 'ispermanent'
            spred.value = pred['value'] == 'permanent'
        elif pred['field'] == 'format':
            logger.debug("L291 format is " + str(pred['value']))
            format_lookup = Format.objects.filter(format__iexact=pred['value']).first()
            if format_lookup is None:
                spred.value = -1
            else:
                spred.value = format_lookup.id
        spreds.append(spred)
        latest_time = time.time()
        logger.debug("L325 {}".format(str(latest_time - start_time)))

    if request.GET.get('sort', False):
        sort_order = request.GET.get('sort', 'name')
        request.session['sort_order'] = sort_order

    latest_time = time.time()
    logger.debug("L332 {}".format(str(latest_time - start_time)))

    sort_by_filing_name_added = False
    if request.session.get('sort_order', False):
        sort_order = request.session.get('sort_order')
        sd = SortDirective()
        sd.term = 'name'
        if sort_order == 'cmc':
            sd.term = 'cmc'
        elif sort_order.startswith('rating-'):
            ffff = Format.objects.filter(format__iexact=sort_order.replace('rating-', '')).first()
            logger.debug("L308 SORT ORDER is '{}' from sort param '{}'".format(str(ffff), sort_order))
            if ffff is not None:
                sd.term = 'cardrating'
                sd.direction = sd.DESC
                sd.crs_format_id = ffff.id
        else:
            sort_by_filing_name_added = True
        spreds.append(sd)

    latest_time = time.time()
    logger.debug("L355 {}".format(str(latest_time - start_time)))

    # Let's make sure to always sort by filing_name as the last
    # condition. If we do not, then MySQL (and any SQL RDBMS, I
    # imagine) will return an undefined sort order when order by
    # values that have multiple records that are equal. For instance,
    # if we sort by CMC, there could be pages and pages of CMC=3, and
    # the sort order within that set is undefined, thus paginating
    # within the list (which makes another SQL query) may return the
    # same results over and over again. Adding a secondary sort that
    # we know is unique in value will solve that.
    if not sort_by_filing_name_added:
        sd = SortDirective()
        sd.term = 'name'
        spreds.append(sd)

    latest_time = time.time()
    logger.debug("L372 {}".format(str(latest_time - start_time)))

    cache_key_base = u'{},{}'.format(str([xx['hint'] for xx in query_pred_array]), request.session.get('sort_order'))
    cache_key_base = cache_key_base.replace(u' ', u'_')
    cache_key_list = 'cl:{}'.format(cache_key_base)
    cache_key_page = 'cp:{}'.format(cache_key_base)
    card_list = cache.get(cache_key_list)
    logger.debug("L379 cache returned {} for {}".format(str(card_list is not None), cache_key_list))
    if card_list is None:
        latest_time = time.time()
        logger.debug("L382 {}".format(str(latest_time - start_time)))
        card_list = Card.playables.search(spreds)
        cache.set(cache_key_list, card_list, settings.CARDS_SEARCH_CACHE_TIME)

    latest_time = time.time()
    logger.debug("L387 {}".format(str(latest_time - start_time)))
    list_for_paging = cache.get(cache_key_page)
    logger.debug("L389 cache returned {} for {}".format(str(list_for_paging is not None), cache_key_page))

    if list_for_paging is None:
        list_for_paging = list(card_list)
        cache.set(cache_key_page, list_for_paging, settings.CARDS_SEARCH_CACHE_TIME)

    logger.debug("L395 card list is {}".format(str(len(list_for_paging))))
    latest_time = time.time()
    logger.debug("L387 {}".format(str(latest_time - start_time)))

    paginator = Paginator(list_for_paging, 25)
    page = request.GET.get('page', request.session.get("curpage", 1))

    latest_time = time.time()
    logger.debug("L403 {}".format(str(latest_time - start_time)))
    try:
        cards = paginator.page(page)
        request.session["curpage"] = page
    except PageNotAnInteger:
        cards = paginator.page(1)
        request.session["curpage"] = 1
    except EmptyPage:
        cards = paginator.page(paginator.num_pages)
        request.session["curpage"] = paginator.num_pages

    latest_time = time.time()
    logger.debug("L415 {}".format(str(latest_time - start_time)))

    context = {
        'ellided_prev_page': max(0, int(page) - 4),
        'ellided_next_page': min(paginator.num_pages, int(page) + 4),
        'cards': cards,
        'thepagetitle': page_title,
        'sort_order': request.session.get('sort_order', 'name'),
        'predicates': query_pred_array,
        'predicates_js': json.dumps(query_pred_array),
        'CARDS_SEARCH_CACHE_TIME': settings.CARDS_SEARCH_CACHE_TIME,
        'cache_key_page': cache_key_page,
    }

    latest_time = time.time()
    logger.debug("L430 {}".format(str(latest_time - start_time)))

    context['current_formats'] = Format.objects.filter(start_date__lte=datetime.today(),
                                                       end_date__gte=datetime.today()).order_by('format')

    latest_time = time.time()
    logger.debug("L436 {}".format(str(latest_time - start_time)))

    httpResp = render(request, 'cards/list.html', context)

    latest_time = time.time()
    logger.debug("L441 {}".format(str(latest_time - start_time)))

    return httpResp


def detail(request, multiverseid=None, slug=None):
    logger = logging.getLogger(__name__)
    cards = []
    primary_basecard_id = None
    try:
        if multiverseid is not None:
            cards = Card.objects.filter(
                multiverseid=multiverseid).order_by('card_number')
            primary_basecard_id = cards[0].basecard.id
        elif slug is not None:
            slugws = slug.lower().replace('-', ' ')
            cards = Card.objects.filter(
                basecard__filing_name=slugws).order_by('card_number')
            if len(cards) > 0:
                multiverseid = cards[0].multiverseid
                return redirect(
                    'cards:detail',
                    permanent=True,
                    multiverseid=multiverseid,
                    slug=slug)
            else:
                raise Http404
        else:
            raise Http404
    except Card.DoesNotExist:
        raise Http404

    # Let's see if the slub matching my filing name
    if slug is not None:
        slugws = slug.lower().replace('-', ' ')
        logger.debug("slug is now \"" + slugws + "\"")
        amatch = False
        for acard in cards:
            if amatch:
                break
            amatch = amatch or (slugws == acard.basecard.filing_name)
        if not amatch:
            raise Http404
    elif not request.is_ajax():
        # we have a card with a filing_name, let's just redirect them...
        # But only redirect if it is NOT an ajax request. Let's make it easy on
        # our ajax friends.
        newslug = cards[0].basecard.filing_name.replace(' ', '-')
        return redirect(
            'cards:detail',
            permanent=True,
            multiverseid=multiverseid,
            slug=newslug)

    backCards = []
    if len(cards) > 0:
        backCards = Card.objects.filter(
            basecard__physicalcard__id=cards[0].basecard.physicalcard.id,
            expansionset__id=cards[0].expansionset.id)
        logger.error(backCards)
    cards = cards | backCards
    twinCards = Card.objects.filter(
        basecard__id=cards[0].basecard.id).order_by('multiverseid')
    response = HttpResponse("Lame. Something must be broken.")
    jcards = []
    card_list = []
    card_titles = []
    for card in cards:
        #logger.error('rules text: ' + card.rules_text_html())
        if card.basecard.name in card_titles:
            continue
        card_titles.append(card.basecard.name)

        if request.is_ajax():
            response_dict = {}
            jcard = {
                'name': card.basecard.name,
                'mana_cost': card.basecard.mana_cost,
                'mana_cost_html': card.mana_cost_html(),
                'type': [
                    tt.type for tt in card.basecard.types.all()],
                'supertype': [
                    spt.supertype for spt in card.basecard.supertypes.all()],
                'subtype': [
                    st.subtype for st in card.basecard.subtypes.all()],
                'text': card.rules_text_html(),
                'flavor_text': card.flavor_text,
                'mark': '',
                'cmc': card.basecard.cmc,
                'multiverseid': card.multiverseid,
                'expansionset': {
                    'name': card.expansionset.name,
                    'abbr': card.expansionset.abbr},
                'rarity': card.rarity.rarity,
                'card_number': card.card_number,
                'img_url': card.img_url(),
                'power': card.basecard.power,
                'toughness': card.basecard.toughness,
                'loyalty': card.basecard.loyalty,
                'colors': [
                    cc.color for cc in card.basecard.colors.all()]}
            try:
                if card.mark is not None:
                    jcard['mark'] = card.mark.mark
            except Mark.DoesNotExist:
                1
                #jcard.mark = ''
            jcards.append(jcard)
        card_list.append({'card': card, })

    if request.is_ajax():
        response_dict.update({'status': 'success',
                              'physicalCardTitle': card.basecard.physicalcard.get_card_name(),
                              'cards': jcards,
                              })
        response = HttpResponse(
            json.dumps(response_dict),
            content_type='application/javascript')
    else:
        card_stats = []
        mod_fcstat = None
        std_fcstat = None
        edh_fcstat = None
        cpw_cache_key = 'pc-{}_cpw'.format(str(cards[0].basecard.physicalcard.id))
        cpw_cache_update_needed = False
        card_playedwiths = cache.get(cpw_cache_key, dict())
        formats = Format.cards.current_legal_formats(cards[0])
        card_format_details = {}

        # this is the amount of time that we are going to look back for decks in formats
        two_years_ago = datetime.now() - timedelta(days=2 * 365)

        for ff in formats:
            dets = {}
            card_format_details[ff.format] = dets
            dets['format'] = ff
            if ff.formatname == 'Standard':
                std_fcstat = FormatCardStat.objects.filter(physicalcard=cards[0].basecard.physicalcard, format=ff).first()
                card_stats.append(std_fcstat)
            elif ff.formatname == 'Modern':
                mod_fcstat = FormatCardStat.objects.filter(physicalcard=cards[0].basecard.physicalcard, format=ff).first()
                card_stats.append(mod_fcstat)
            elif ff.formatname == 'Commander':
                edh_fcstat = FormatCardStat.objects.filter(physicalcard=cards[0].basecard.physicalcard, format=ff).first()
                card_stats.append(edh_fcstat)
            if ff.formatname not in card_playedwiths:
                card_playedwiths[
                    ff.formatname] = cards[0].basecard.physicalcard.find_played_with_cards(
                    Format.objects.filter(
                        formatname=ff.formatname,
                        start_date__gte=two_years_ago))
                cpw_cache_update_needed = True
            dets['rating'] = cards[0].basecard.physicalcard.cardrating_set.filter(test_id=1, format_id=ff.id).first()
            dets['wincount'] = Battle.objects.filter(winner_pcard=cards[0].basecard.physicalcard, test_id=1, format_id=ff.id).count()
            dets['losecount'] = Battle.objects.filter(loser_pcard=cards[0].basecard.physicalcard, test_id=1, format_id=ff.id).count()
            dets['battlecount'] = dets['wincount'] + dets['losecount']
            if dets['battlecount'] > 0:
                dets['winpercentage'] = 100 * float(dets['wincount']) / float(dets['battlecount'])
                dets['losepercentage'] = 100 * float(dets['losecount']) / float(dets['battlecount'])
            else:
                dets['winpercentage'] = 'n/a'
                dets['losepercentage'] = 'n/a'
            won_battles = Battle.objects.filter(winner_pcard=cards[0].basecard.physicalcard, test_id=1, format_id=ff.id).values(
                'loser_pcard_id').annotate(num_wins=Count('loser_pcard_id')).order_by('-num_wins')[:6]
            dets['card_wins'] = [
                Card.objects.filter(
                    basecard__physicalcard__id=battle['loser_pcard_id']).order_by('-multiverseid').first() for battle in won_battles]
            lost_battles = Battle.objects.filter(loser_pcard=cards[0].basecard.physicalcard, test_id=1, format_id=ff.id).values(
                'winner_pcard_id').annotate(num_losses=Count('winner_pcard_id')).order_by('-num_losses')[:6]
            dets['card_losses'] = [
                Card.objects.filter(
                    basecard__physicalcard__id=battle['winner_pcard_id']).order_by('-multiverseid').first() for battle in lost_battles]

        if cpw_cache_update_needed:
            cache.set(cpw_cache_key, card_playedwiths, 60 * 60 * 24)

        similars = cards[0].basecard.physicalcard.find_similar_cards()

        associations = Association.objects.filter(associationcards=cards[0].basecard.physicalcard)

        response = render(request, 'cards/detail.html', {'request_mvid': multiverseid,
                                                         'primary_basecard_id': primary_basecard_id,
                                                         'cards': card_list,
                                                         'keywords': cards[0].basecard.physicalcard.cardkeyword_set.all().order_by('-kwscore'),
                                                         'similars': similars,
                                                         'other_versions': twinCards,
                                                         'physicalCardTitle': cards[0].basecard.physicalcard.get_card_name(),
                                                         'card_format_details': card_format_details,
                                                         'physicalcard': cards[0].basecard.physicalcard,
                                                         'associations': associations,
                                                         'rulings': cards[0].basecard.get_rulings(),
                                                         'mod_card_stat': mod_fcstat,
                                                         'std_card_stat': std_fcstat,
                                                         'edh_card_stat': edh_fcstat,
                                                         'card_playedwiths': card_playedwiths,
                                                         'card_stats': card_stats,
                                                         #'rules_text_html': mark_safe(card.basecard.rules_text),
                                                         #'flavor_text_html': mark_safe(card.flavor_text),
                                                         #'mana_cost_html': mana_cost_html,
                                                         #'img_url': img_url, })
                                                         })
    return response


def cardstats(request, formatname=None, physicalcard_id=None, multiverseid=None):
    result = dict()
    result['type'] = 'CardStatusResponse'
    result['status'] = 'ok'
    latest_format = None
    if formatname is None:
        result['status'] = 'error'
        result['status_message'] = 'format not specified'
    else:
        latest_format = Format.objects.filter(formatname=formatname).order_by('-start_date').first()
        if latest_format is None:
            result['status'] = 'error'
            result['status_message'] = 'format could not be found'

    pcard = None
    if result['status'] == 'ok':
        if physicalcard_id is not None:
            try:
                pcard = PhysicalCard.objects.get(pk=physicalcard_id)
            except PhysicalCard.DoesNotExist:
                result['status'] = 'error'
                result['status_message'] = 'card cannot be found'
        elif multiverseid is not None:
            card = Card.objects.filter(multiverseid=multiverseid).first()
            if card is not None:
                pcard = card.basecard.physicalcard
            else:
                result['status'] = 'error'
                result['status_message'] = 'card cannot be found'
    if result['status'] == 'ok':
        fffs = Format.objects.filter(formatname=latest_format.formatname, start_date__gt=datetime(2013, 9, 15)).order_by('start_date')
        stats = list()
        for fff in fffs:
            fcstat = FormatCardStat.objects.filter(
                physicalcard=pcard,
                format=fff).first()
            rec = dict()
            if fcstat is None:
                rec['format'] = fff.format
                rec['format_start_date'] = fff.start_date.strftime('%Y-%m-%d')
                rec['occurence_count'] = 0
                rec['deck_count'] = 0
                rec['average_card_count_in_deck'] = 0
                rec['percentage_of_all_cards'] = 0
                rec['in_decks_percentage'] = 0
                rec['meets_staple_threshold'] = False
            else:
                rec['format'] = fcstat.format.format
                rec['format_start_date'] = fcstat.format.start_date.strftime('%Y-%m-%d')
                rec['occurence_count'] = fcstat.occurence_count
                rec['deck_count'] = fcstat.deck_count
                rec['average_card_count_in_deck'] = fcstat.average_card_count_in_deck
                rec['percentage_of_all_cards'] = fcstat.percentage_of_all_cards
                rec['in_decks_percentage'] = fcstat.in_decks_percentage()
                rec['meets_staple_threshold'] = fcstat.percentage_of_all_cards > FormatCardStat.STAPLE_THRESHOLD

            stats.append(rec)
        # card_stats.append(mod_fcstat)
        result['stats'] = stats
    the_data = json.dumps(result)
    if 'callback' in request.GET or 'callback' in request.POST:
        # a jsonp response!
        callback_request = None
        if 'callback' in request.GET:
            callback_request = request.GET['callback']
        elif 'callback' in request.POST:
            callback_request = request.POST['callback']
        the_data = '%s(%s);' % (callback_request, the_data)
        return HttpResponse(the_data, "text/javascript")
    else:
        return HttpResponse(the_data, content_type='application/json')
    pass


def formats(request, formatname="modern"):
    context = dict()
    context['formats'] = Format.objects.filter(start_date__lte=datetime.today(),
                                               end_date__gte=datetime.today())

    response = render(request, 'cards/formats.html', context)
    return response


def formatstats(request, formatname="modern"):
    context = dict()
    top_formats = Format.objects.filter(formatname__iexact=formatname).order_by('-start_date')
    top_format = None
    next_format = None
    try:
        top_format = top_formats[0]
        next_format = top_formats[1]
    except IndexError:
        raise Http404
    context['formatname'] = top_format.formatname
    up_raw_sql = '''
SELECT s1.physicalcard_id AS id,
       100 * s2.percentage_of_all_cards AS prev_percentage,
       100 * s1.percentage_of_all_cards AS current_percentage,
       100 * (s1.percentage_of_all_cards - s2.percentage_of_all_cards) AS delta,
       case when s2.percentage_of_all_cards = 0 then NULL else 100 * (s1.percentage_of_all_cards - s2.percentage_of_all_cards) / s2.percentage_of_all_cards end AS per_change,
       100 * (s1.deck_count / fs1.tournamentdeck_count) decks_current_percentage,
       100 * (s2.deck_count / fs2.tournamentdeck_count) decks_prev_percentage,
       case when fs2.tournamentdeck_count = 0 then NULL else 100 * ((s1.deck_count / fs1.tournamentdeck_count) - (s2.deck_count / fs2.tournamentdeck_count)) / (s2.deck_count / fs2.tournamentdeck_count) end AS decks_per_change
  FROM formatcardstat s1
       JOIN basecard bc ON s1.physicalcard_id = bc.physicalcard_id AND bc.cardposition IN ('F','L','U')
       JOIN formatstat fs1 ON fs1.format_id = s1.format_id AND s1.format_id = %s
       LEFT JOIN formatcardstat s2 ON s1.physicalcard_id = s2.physicalcard_id AND s2.format_id = %s
       LEFT JOIN formatstat fs2 ON fs2.format_id = s2.format_id
 WHERE s1.percentage_of_all_cards > s2.percentage_of_all_cards
 ORDER BY delta DESC LIMIT 50'''

    foo = PhysicalCard.objects.raw(up_raw_sql, [top_format.id, next_format.id])
    up_cr = CardRating.objects.filter(test_id=1, format=top_format, physicalcard_id__in=[g.id for g in foo])
    context['trendingup'] = foo
    context['trendingup_cr'] = up_cr

    down_raw_sql = '''
SELECT s1.physicalcard_id AS id,
       100 * s2.percentage_of_all_cards AS prev_percentage,
       100 * s1.percentage_of_all_cards AS current_percentage,
       100 * (s2.percentage_of_all_cards - s1.percentage_of_all_cards) AS delta,
       case when s2.percentage_of_all_cards = 0 then NULL else 100 * (((s2.percentage_of_all_cards - s1.percentage_of_all_cards) / s2.percentage_of_all_cards) - 1) end AS per_change,
       100 * (s1.deck_count / fs1.tournamentdeck_count) decks_current_percentage,
       100 * (s2.deck_count / fs2.tournamentdeck_count) decks_prev_percentage,
       case when fs2.tournamentdeck_count = 0 then NULL else 100 * ((s1.deck_count / fs1.tournamentdeck_count) - (s2.deck_count / fs2.tournamentdeck_count)) / (s2.deck_count / fs2.tournamentdeck_count) end AS decks_per_change
  FROM formatcardstat s1
       JOIN basecard bc ON s1.physicalcard_id = bc.physicalcard_id AND bc.cardposition IN ('F','L','U')
       JOIN formatstat fs1 ON fs1.format_id = s1.format_id AND s1.format_id = %s
       LEFT JOIN formatcardstat s2 ON s1.physicalcard_id = s2.physicalcard_id AND s2.format_id = %s
       LEFT JOIN formatstat fs2 ON fs2.format_id = s2.format_id
 WHERE s1.percentage_of_all_cards < s2.percentage_of_all_cards
 ORDER BY delta DESC LIMIT 50'''
    tdown = PhysicalCard.objects.raw(down_raw_sql, [top_format.id, next_format.id])
    down_cr = CardRating.objects.filter(test_id=1, format=top_format, physicalcard_id__in=[g.id for g in tdown])
    context['trendingdown'] = tdown
    context['trendingdown_cr'] = down_cr

    top_raw_sql = '''
SELECT s1.physicalcard_id AS id,
       100 * s2.percentage_of_all_cards AS prev_percentage,
       100 * s1.percentage_of_all_cards AS current_percentage,
       100 * (s2.percentage_of_all_cards - s1.percentage_of_all_cards) AS delta,
       case when s2.percentage_of_all_cards = 0 then NULL else 100 * (((s2.percentage_of_all_cards - s1.percentage_of_all_cards) / s2.percentage_of_all_cards) - 1) end AS per_change,
       100 * (s1.deck_count / fs1.tournamentdeck_count) decks_current_percentage,
       100 * (s2.deck_count / fs2.tournamentdeck_count) decks_prev_percentage,
       case when fs2.tournamentdeck_count = 0 then NULL else 100 * ((s1.deck_count / fs1.tournamentdeck_count) - (s2.deck_count / fs2.tournamentdeck_count)) / (s2.deck_count / fs2.tournamentdeck_count) end AS decks_per_change
  FROM formatcardstat s1
       JOIN basecard bc ON s1.physicalcard_id = bc.physicalcard_id AND s1.format_id = %s AND bc.cardposition IN ('F','L','U')
       JOIN formatstat fs1 ON fs1.format_id = s1.format_id
       LEFT JOIN formatcardstat s2 ON s1.physicalcard_id = s2.physicalcard_id AND s2.format_id = %s
       LEFT JOIN formatstat fs2 ON fs2.format_id = s2.format_id
 ORDER BY s1.percentage_of_all_cards DESC LIMIT 100'''
    top = PhysicalCard.objects.raw(top_raw_sql, [top_format.id, next_format.id])
    top_cr = CardRating.objects.filter(test_id=1, format=top_format, physicalcard_id__in=[g.id for g in top])
    context['top'] = top
    context['top_cr'] = top_cr

    response = render(request, 'cards/formatstats.html', context)
    return response


def battle(request, format="redirect"):
    logger = logging.getLogger(__name__)
    # this shows two cards at random and then let's the user decide which one
    # is better.

    # If there was no format on the URL, then let's push it to Standard.
    if format == "redirect":
        return redirect('cards:battle', format="standard")

    # REVISIT - need real exception handling here!!
    format_obj = Format.objects.filter(
        formatname__iexact=format,
        start_date__lte=datetime.today(),
        end_date__gte=datetime.today()).order_by('-end_date').first()
    format_id = format_obj.id

    # Only contemplating one test right now. This is the id of the battletest table in the database.
    test_id = 1

    # Going straight to the DB on this...
    cursor = connection.cursor()

    # this is a set of parameters that are going to be common among queries that select for cards.
    query_params = {'formatid': str(format_id),
                    'layouts': [PhysicalCard.NORMAL, PhysicalCard.SPLIT, PhysicalCard.FLIP, PhysicalCard.DOUBLE, PhysicalCard.LEVELER]}

    card_a = None
    first_card = {
        'mu': 25.0,
        'sigma': 25.0 / 3.0,
    }
    card_b = None
    second_card = {
        'mu': 25.0,
        'sigma': 25.0 / 3.0,
    }
    find_iterations = 0

    rand_source = 'random'

    # this is a BATTLE CHEAT so that you can battle a specific card
    if request.GET.get('muid', False) or request.session.get('battle_cont_muid', False) or request.GET.get('bcid', False):
        if request.GET.get('bcid', False):
            card_a = Card.objects.filter(basecard__id__exact=int(request.GET.get('bcid', 1))).order_by('-multiverseid').first()
        else:
            card_a = Card.objects.filter(multiverseid__exact=request.GET.get('muid', request.session.get('battle_cont_muid'))).first()
        rand_source = 'querystring'
        first_card['basecard_id'] = card_a.basecard.id
        first_card['physicalcard_id'] = card_a.basecard.physicalcard.id
        crsdb = CardRating.objects.filter(
            physicalcard=card_a.basecard.physicalcard,
            test__id__exact=test_id,
            format=format_obj)
        try:
            crdb = crsdb[0]
            first_card['mu'] = crdb.mu
            logger.debug("L756 Setting first card mu to {}".format(str(crdb.mu)))
            first_card['sigma'] = crdb.sigma
        except IndexError:
            # no op
            logger.error("Battle: bad ju-ju finding card ratings for physicalcard id " + str(card_a.basecard.physicalcard.id))
            pass
    else:
        fcsqls_xtra = ''
        bb_file = 'betterbattle_{}.csv'.format(str(format_id))
        try:
            bb_file = settings.BETTER_BATTLE_PATH + '/' + 'betterbattle_{}.csv'.format(str(format_id))
        except AttributeError:
            pass
        #logger.error("cur dir " + os.path.abspath("."))
        #logger.error("looking for  " + os.path.abspath(bb_file))
        if os.path.isfile(bb_file):
            #logger.error("loaded " + os.path.abspath(bb_file))
            rand_source = "file: " + os.path.abspath(bb_file)
            bb_ids_list = list()
            with open(bb_file) as bb_f:
                bbcontent = bb_f.readlines()
                for bbline in bbcontent:
                    try:
                        bb_ids_list.append(int(bbline.strip()))
                    except ValueError:
                        pass
            query_params['x_ids'] = bb_ids_list
            if len(bb_ids_list) > 0:
                fcsqls_xtra = ' AND pc.id IN %(x_ids)s '
        fcsqls = 'SELECT fbc.basecard_id, cr.mu, cr.sigma, bc.physicalcard_id, RAND() r FROM formatbasecard fbc JOIN basecard bc ON bc.id = fbc.basecard_id JOIN cardrating cr ON cr.physicalcard_id = bc.physicalcard_id AND cr.format_id = fbc.format_id JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE pc.layout IN %(layouts)s AND fbc.format_id = %(formatid)s {} ORDER BY cr.sigma DESC, r ASC LIMIT 1'.format(
            fcsqls_xtra)
        #logger.error("First Card SQL: " + fcsqls)
        cursor.execute(fcsqls, params=query_params)
        rows = cursor.fetchall()
        first_card = {
            'basecard_id': rows[0][0],
            'mu': rows[0][1],
            'sigma': rows[0][2],
            'physicalcard_id': rows[0][3],
        }
        logger.debug("L795 Setting first card mu to {}".format(str(first_card['mu'])))
        card_a = PhysicalCard.objects.get(pk=first_card['physicalcard_id']).get_latest_card()

    query_params['cardabcid'] = first_card['basecard_id']
    query_params['cardapcid'] = first_card['physicalcard_id']
    while card_b is None:
        simcard_max_results = 25 + (10 * find_iterations)
        query_params['lowermu'] = first_card['mu'] - ((1 + find_iterations) * first_card['sigma'])
        query_params['uppermu'] = first_card['mu'] + ((1 + find_iterations) * first_card['sigma'])
        # now let's get a card of similar level - make it a real battle
        sqls = ''

        if random.random() < 0.66:
            # 2/3 of the time, let's pick a random card
            #sqls = 'SELECT fbc.basecard_id, cr.mu, cr.sigma, RAND() r FROM formatbasecard fbc JOIN basecard bc ON bc.id = fbc.basecard_id JOIN cardrating cr ON cr.physicalcard_id = bc.physicalcard_id AND cr.format_id = fbc.format_id JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE fbc.format_id = %(formatid)s AND fbc.basecard_id <> %(cardabcid)s AND cr.mu > %(lowermu)s AND cr.mu < %(uppermu)s AND pc.layout IN %(layouts)s ORDER BY r ASC LIMIT 1'
            sqls = 'SELECT fbc.basecard_id, cr.mu, cr.sigma, pc.id, RAND() r FROM formatbasecard fbc JOIN basecard bc ON bc.id = fbc.basecard_id JOIN cardrating cr ON cr.physicalcard_id = bc.physicalcard_id AND cr.format_id = fbc.format_id JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE fbc.format_id = %(formatid)s AND fbc.basecard_id <> %(cardabcid)s AND cr.mu > %(lowermu)s AND cr.mu < %(uppermu)s AND pc.layout IN %(layouts)s ORDER BY r ASC LIMIT 1'
        else:
            # 1/3 of the time, let's pick a card that is similar and in this format
            logger.debug("L806 Picking an opponent to {} based on simliar cards.".format(str(first_card['basecard_id'])))
            query_params['similar_pcard_ids'] = card_a.basecard.physicalcard.find_similar_card_ids(max_results=simcard_max_results)
            #sqls = 'SELECT sbc.id, cr.mu, cr.sigma, bc.physicalcard_id, RAND() r FROM similarphysicalcard AS spc JOIN basecard bc ON spc.physicalcard_id = bc.physicalcard_id JOIN basecard sbc ON sbc.physicalcard_id = spc.sim_physicalcard_id AND sbc.cardposition IN (\'F\',\'L\',\'T\') JOIN formatbasecard simfbc ON sbc.id = simfbc.basecard_id AND simfbc.format_id = %(formatid)s JOIN cardrating cr ON cr.physicalcard_id = sbc.physicalcard_id AND cr.format_id = simfbc.format_id  WHERE bc.cardposition IN (\'F\',\'L\',\'T\') AND bc.id = %(cardabcid)s ORDER BY r ASC LIMIT 1'
            sqls = '''SELECT bc.id, cr.mu, cr.sigma, pc.id, RAND() r FROM physicalcard AS pc JOIN cardrating AS cr ON cr.physicalcard_id = pc.id JOIN basecard bc ON bc.physicalcard_id = pc.id JOIN formatbasecard AS fbc ON fbc.basecard_id = bc.id WHERE fbc.format_id = %(formatid)s AND pc.id IN %(similar_pcard_ids)s ORDER BY r ASC LIMIT 1'''
        logger.debug("Second Card SQL: " + sqls)
        cursor.execute(sqls, params=query_params)
        rows = cursor.fetchall()
        try:
            second_card = {
                'basecard_id': rows[0][0],
                'mu': rows[0][1],
                'sigma': rows[0][2],
                'physicalcard_id': rows[0][3],
            }
            #logger.debug("L813 Setting second card mu to {}".format(str(second_card['mu'])))
        except IndexError:
            logger.error("Battle iteration " + str(find_iterations) + ": UGH. IndexError. This SQL returned no result: " + sqls)
            logger.error("Battle: params were: " + str(query_params))
            # so let's just iterate this one again...
            find_iterations = find_iterations + 1
            continue
        logger.debug("L845 Second card is {}.".format(json.dumps(second_card)))
        #card_b_list = Card.objects.filter(basecard__id__exact=rows[1][0]).order_by('-multiverseid')
        #card_b = Card.objects.filter(basecard__id__exact=second_card['basecard_id']).order_by('-multiverseid').first()
        card_b = PhysicalCard.objects.get(pk=second_card['physicalcard_id']).get_latest_card()

        # lastly, let's check to make sure that this battle has not already occured
        sqls = "SELECT 1 FROM battle WHERE session_key = '" + str(
            request.session.session_key) + "' AND ((winner_pcard_id = " + str(
            card_a.basecard.physicalcard.id) + " AND loser_pcard_id = " + str(
            card_b.basecard.physicalcard.id) + ") OR (winner_pcard_id = " + str(
                card_b.basecard.physicalcard.id) + " AND loser_pcard_id = " + str(
                    card_a.basecard.physicalcard.id) + "))"
        #'request.session.fbc.basecard_id, cr.mu, cr.sigma, RAND() r FROM formatbasecard fbc JOIN basecard bc ON bc.id = fbc.basecard_id JOIN cardrating cr ON cr.physicalcard_id = bc.physicalcard_id WHERE fbc.format_id = ' + str(format_id) + ' AND fbc.basecard_id <> ' + str(first_card['basecard_id']) + ' AND cr.mu > ' + str(first_card['mu'] - ((1 + find_iterations) * first_card['sigma'])) + ' AND cr.mu < ' + str(first_card['mu'] + ((1 + find_iterations) * first_card['sigma'])) + ' ORDER BY r ASC LIMIT 1'
        #logger.error("Check battle SQL: " + sqls)
        cursor.execute(sqls)
        rows = cursor.fetchall()
        if len(rows) > 0 and find_iterations < 9:
            # we have done this battle before! Oops!
            card_b = None
            find_iterations = find_iterations + 1

        if find_iterations > 10:
            logger.error("Battle iteration " +
                         str(find_iterations) +
                         ": Unable to continue looking for a valid card. Let's give up and let the user know. basecard.id = " +
                         str(query_params['cardabcid']) +
                         ", sessions_key = " +
                         str(request.session.session_key))
            break

    # REVISIT - we need to handle the fact that card_b may be None!!!

    # Let's insure that we are looking at the right part of the physical card...
    if card_a.basecard.cardposition not in [BaseCard.FRONT, BaseCard.LEFT, BaseCard.UP]:
        card_a = PhysicalCard.objects.get(pk=card_a.basecard.physicalcard.id).get_latest_card()
    if card_b.basecard.cardposition not in [BaseCard.FRONT, BaseCard.LEFT, BaseCard.UP]:
        card_b = PhysicalCard.objects.get(pk=card_b.basecard.physicalcard.id).get_latest_card()

    context = {'card_a': card_a,
               'card_b': card_b,
               'first_card': first_card,
               'second_card': second_card,
               'test_id': test_id,
               'format_id': format_id,
               'format': format_obj,
               'rand_source': rand_source,
               }
    if random.random() > 0.5:
        y_a = context['card_a']
        context['card_a'] = context['card_b']
        context['card_b'] = y_a
        y_c = context['first_card']
        context['first_card'] = context['second_card']
        context['second_card'] = y_c

    if request.GET.get(
            'c',
            False) or request.session.get(
            'battle_cont_muid',
            False):
        # let's keep card_a in rotation
        context['continue_muid'] = card_a.multiverseid
        context['continue_muid_qs'] = '&muid=' + str(card_a.multiverseid)
        # get this out of the session. we only needed it for one page turn. The
        # next page will pass a query param if it wants it.
        if 'battle_cont_muid' in request.session:
            del request.session['battle_cont_muid']
    response = render(request, 'cards/battle.html', context)
    return response


def winbattle(request):
    # There is no error checking in here yet. Needs to be tested off of the
    # happy path!
    logger = logging.getLogger(__name__)
    winning_card = None
    losing_card = None
    format = None
    format_nick = 'standard'
    test = None
    if request.GET.get('winner', False):
        card_w_list = Card.objects.filter(
            multiverseid__exact=request.GET.get(
                'winner',
                0))
        winning_card = card_w_list[0]
    if request.GET.get('loser', False):
        card_l_list = Card.objects.filter(
            multiverseid__exact=request.GET.get(
                'loser',
                0))
        losing_card = card_l_list[0]
    if request.GET.get('format_id', False):
        format = Format.objects.get(pk=request.GET.get('format_id'))
        format_nick = format.formatname.lower()
    if request.GET.get('test_id', False):
        test = BattleTest.objects.get(pk=request.GET.get('test_id'))

    #logger.error("winner physical: " + str(winning_card.basecard.physicalcard.id))
    #logger.error("loser physical: " + str(losing_card.basecard.physicalcard.id))
    #logger.error("format: " + str(format))
    #logger.error("test: " + str(test))
    #logger.error("session: " + request.session.session_key)
    battle = Battle(test=test,
                    format=format,
                    winner_pcard=winning_card.basecard.physicalcard,
                    loser_pcard=losing_card.basecard.physicalcard,
                    session_key=request.session.session_key)
    try:
        battle.save()
    except IntegrityError as ie:
        logger.error("Integrity Error on winning a battle... probably not a big deal: {}".format(str(ie)))

    updateRatings(battle)

    request.session['battle_cont_muid'] = request.GET.get('muid', False)
    return redirect('cards:battle', format=format_nick)


def updateRatings(battle):
    logger = logging.getLogger(__name__)
    ts = TrueSkill(backend='mpmath')
    crdb_w = None
    crdb_l = None
    rating_w = None
    rating_l = None

    crsdb_w = CardRating.objects.filter(
        physicalcard__id__exact=battle.winner_pcard.id,
        test__id__exact=battle.test.id,
        format__id__exact=battle.format.id)
    try:
        crdb_w = crsdb_w[0]
        rating_w = Rating(mu=crdb_w.mu, sigma=crdb_w.sigma)
    except IndexError:
        # well, that isn't good. Just be done with it. The cron job will fix it
        # later.
        logger.error("updateRatings - could not get the CardRating for the winner. battle = {}".format(str(battle)))
        return

    crsdb_l = CardRating.objects.filter(
        physicalcard__id__exact=battle.loser_pcard.id,
        test__id__exact=battle.test.id,
        format__id__exact=battle.format.id)
    try:
        crdb_l = crsdb_l[0]
        rating_l = Rating(mu=crdb_l.mu, sigma=crdb_l.sigma)
    except IndexError:
        # well, that isn't good. Just be done with it. The cron job will fix it
        # later.
        logger.error("updateRatings - could not get the CardRating for the loser. battle = {}".format(str(battle)))
        return

    # calculate!
    logger.error("updating battles for cards {} and {}".format(str(battle.winner_pcard.id), str(battle.loser_pcard.id)))
    rating_w, rating_l = rate_1vs1(rating_w, rating_l, env=ts)

    # save
    crdb_w.mu = rating_w.mu
    crdb_w.sigma = rating_w.sigma
    crdb_w.save()
    crdb_l.mu = rating_l.mu
    crdb_l.sigma = rating_l.sigma
    crdb_l.save()

    return


def vote(request, multiverseid):
    return HttpResponse("You're voting on card %s." % multiverseid)


def ratings(request, format_id=0):
    logger = logging.getLogger(__name__)
    if format_id is None or format_id == 0:
        return redirect(
            'cards:ratings',
            permanent=True,
            format_id=1)

    format = get_object_or_404(Format, pk=format_id)

    test_id = 1
    # dummy test harness to just get some ratings...
    context = {}
    context['format'] = format

    context['cards_count'] = FormatBasecard.objects.filter(
        format=format_id).count()

    cursor = connection.cursor()
    wbattle_sql = 'SELECT bc.physicalcard_id AS physicalcard_id, count(b.id) FROM formatbasecard AS fbc JOIN basecard AS bc ON fbc.basecard_id = bc.id LEFT JOIN battle AS b ON b.winner_pcard_id = bc.physicalcard_id AND fbc.format_id = b.format_id WHERE fbc.format_id = ' + \
        format_id + ' GROUP by physicalcard_id ORDER BY physicalcard_id'
    cursor.execute(wbattle_sql)
    wrows = cursor.fetchall()
    lbattle_sql = 'SELECT bc.physicalcard_id AS physicalcard_id, count(b.id) FROM formatbasecard AS fbc JOIN basecard AS bc ON fbc.basecard_id = bc.id LEFT JOIN battle AS b ON b.loser_pcard_id = bc.physicalcard_id AND fbc.format_id = b.format_id WHERE fbc.format_id = ' + \
        format_id + ' GROUP by physicalcard_id ORDER BY physicalcard_id'
    cursor.execute(lbattle_sql)
    lrows = cursor.fetchall()
    battle_results = []
    itcount = 0
    battles_histo = dict()
    for zoo in range(0, 24):
        battles_histo[zoo] = {'count': 0, 'percent': 0.0}
    for wrow in wrows:
        bat_count = wrow[1] + lrows[itcount][1]
        battle_results.append([wrow[0], wrow[1] + lrows[itcount][1], wrow[1], lrows[itcount][1]])
        if bat_count in battles_histo:
            newcount = battles_histo[bat_count]['count'] + 1
            battles_histo[bat_count] = {
                'count': newcount,
                'percent': 100.0 * float(newcount) / context['cards_count']}
        else:
            battles_histo[bat_count] = {'count': 1, 'percent': 100.0 * 1.0 / context['cards_count']}
        itcount = itcount + 1
    context['tester'] = collections.OrderedDict(sorted(battles_histo.items(), key=lambda t: int(t[0])))

    context['battle_count'] = Battle.objects.filter(
        format__id__exact=format_id,
        test__id__exact=test_id).count()
    bc = Battle.objects.filter(
        format__id__exact=format_id,
        test__id__exact=test_id).aggregate(
        Count(
            'session_key',
            distinct=True))
    context['battlers_count'] = bc['session_key__count']
    context['goal'] = int(context['cards_count'] * 1.5)
    context['percent_to_goal'] = 100 * float(context['battle_count']) / context['goal']
    context['battle_possibilities'] = context[
        'cards_count'] * (context['cards_count'] - 1)
    context['battle_percentage'] = float(
        100) * float(context['battle_count']) / float(context['battle_possibilities'])
    context['ratings'] = []

    current = datetime.now()
    ago = current - timedelta(days=7)
    ago = ago.replace(minute=0, second=0, microsecond=0)
    hour = timedelta(hours=1)
    parts = []
    zero_datetimes = []
    for hit in range(0, 7 * 24 + 1):
        parts.append("SELECT '" + str(ago.year) + '-' + str(ago.month) + '-' + str(ago.day) + ' ' + str(ago.hour) + ":00:00' hh ")
        ago = ago + hour
        zero_datetimes.append([ago, 0])

    activity_sql = 'SELECT h.*, count(b.id) FROM ('
    activity_sql = activity_sql + ' UNION ALL '.join(parts) + ') AS h'
    activity_sql = activity_sql + ' LEFT JOIN  battle b '
    activity_sql = activity_sql + "ON CONVERT(DATE_FORMAT(b.battle_date,'%Y-%m-%d-%H:00:00'),DATETIME) = h.hh "
    activity_sql = activity_sql + "AND b.format_id = " + format_id
    activity_sql = activity_sql + " GROUP BY CONVERT(DATE_FORMAT(b.battle_date,'%Y-%m-%d-%H:00:00'),DATETIME)"
    # logger.error(activity_sql)
    cursor.execute(activity_sql)
    acts = cursor.fetchall()
    db_results_datetime = []
    mysql_f = '%Y-%m-%d %H:%M:%S'
    for row in acts:
        db_results_datetime.append([datetime.strptime(row[0], mysql_f), row[1]])
    big_result = []
    for zero_row in zero_datetimes:
        result = zero_row
        for val_row in db_results_datetime:
            if val_row[0] == zero_row[0]:
                result = val_row
        big_result.append({'datehour': result[0], 'count': result[1]})
    # for gg in big_result:
    #    logger.error(str(gg))
    context['activity'] = big_result

    response = render(request, 'cards/ratings.html', context)
    return response
