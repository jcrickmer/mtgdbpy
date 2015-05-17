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

import random
import operator

from cards.models import Card, CardManager, SearchPredicate, SortDirective, BaseCard
from cards.models import Mark
from cards.models import PhysicalCard
from cards.models import Type
from cards.models import Subtype
from cards.models import Format
from cards.models import FormatBasecard
from cards.models import Ruling
from cards.models import Rarity
from cards.models import Battle
from cards.models import BattleTest
from cards.models import CardRating

from decks.models import FormatCardStat, FormatStat

from django.db.models import Q
from datetime import datetime, timedelta

# import the logging library
import logging

from trueskill import TrueSkill, Rating, quality_1vs1, rate_1vs1
from functools import reduce

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
    context['subtypes'] = [st.subtype for st in Subtype.objects.all()]
    context['rarities'] = [{'id': rr.id, 'rarity': rr.rarity}
                           for rr in Rarity.objects.all().order_by('sortorder')]
    context['formats'] = [
        {
            'format': f.format,
            'formatname': f.formatname,
            'start_date': f.start_date} for f in Format.objects.all().order_by('format')]
    context['current_formats'] = [{'format': f.format,
                                   'formatname': f.formatname,
                                   'start_date': f.start_date} for f in Format.objects.filter(start_date__lte=datetime.today(),
                                                                                              end_date__gte=datetime.today()).order_by('format')]
    return render(request, 'cards/index.html', context)


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
    sqs = SearchQuerySet().autocomplete(name_auto=request.GET.get('q', ''))[:15]
    #suggestions = [result.name for result in sqs]
    suggestions = []
    for result in sqs:
        cardname = result.name
        if cardname is not None and len(cardname) > 0:
            cn_bc = BaseCard.objects.filter(name__iexact=cardname).first()
            result = {'name': cardname}
            if cn_bc is not None:
                the_card = cn_bc.physicalcard.get_latest_card()
                result['url'] = reverse('cards:detail', kwargs={'multiverseid': str(the_card.multiverseid), 'slug': the_card.url_slug()})
                suggestions.append(result)
    # Make sure you return a JSON object, not a bare list.
    # Otherwise, you could be vulnerable to an XSS attack.
    the_data = json.dumps(suggestions)
    if 'callback' in request.REQUEST:
        # a jsonp response!
        the_data = '%s(%s);' % (request.REQUEST['callback'], the_data)
        return HttpResponse(the_data, "text/javascript")
    else:
        return HttpResponse(the_data, content_type='application/json')


def cardlist(request):
    # Get an instance of a logger
    logger = logging.getLogger(__name__)
    # logger.error(request)

    # Let's get the array of predicates from the session
    query_pred_array = []
    if request.session.get('query_pred_array', False):
        query_pred_array = request.session.get('query_pred_array')

    spreds = []
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
        elif pred['field'] == 'subtype':
            subtype_lookup = Subtype.objects.filter(subtype__iexact=pred['value']).first()
            if subtype_lookup is None:
                spred.value = -1
            else:
                spred.value = subtype_lookup.id
        elif pred['field'] == 'format':
            logger.error("format is " + str(pred['value']))
            format_lookup = Format.objects.filter(format__iexact=pred['value']).first()
            if format_lookup is None:
                spred.value = -1
            else:
                spred.value = format_lookup.id
        spreds.append(spred)

    sort_by_filing_name_added = False
    if request.session.get('sort_order', False):
        sort_order = request.session.get('sort_order')
        sd = SortDirective()
        sd.term = 'name'
        if sort_order == 'cmc':
            sd.term = 'cmc'
        elif sort_order.startswith('rating-'):
            ffff = Format.objects.filter(format__iexact=sort_order.replace('rating-', '')).first()
            if ffff is not None:
                sd.term = 'cardrating'
                sd.direction = sd.DESC
                sd.crs_format_id = ffff.id
        else:
            sort_by_filing_name_added = True
        spreds.append(sd)

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

    card_list = Card.playables.search(spreds)

    paginator = Paginator(list(card_list), 25)
    page = request.GET.get('page', request.session.get("curpage", 1))
    try:
        cards = paginator.page(page)
        request.session["curpage"] = page
    except PageNotAnInteger:
        cards = paginator.page(1)
        request.session["curpage"] = 1
    except EmptyPage:
        cards = paginator.page(paginator.num_pages)
        request.session["curpage"] = paginator.num_pages
    context = {
        'ellided_prev_page': max(0, int(page) - 4),
        'ellided_next_page': min(paginator.num_pages, int(page) + 4),
        'cards': cards,
        'sort_order': request.session.get('sort_order', 'name'),
        'predicates': query_pred_array,
        'predicates_js': json.dumps(query_pred_array),
    }
    context['current_formats'] = [{'format': f.format,
                                   'formatname': f.formatname,
                                   'start_date': f.start_date} for f in Format.objects.filter(start_date__lte=datetime.today(),
                                                                                              end_date__gte=datetime.today()).order_by('format')]
    return render(request, 'cards/list.html', context)


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
        logger.error("slug is now \"" + slugws + "\"")
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
                              'physicalCardTitle': " // ".join(card_titles),
                              'cards': jcards,
                              })
        response = HttpResponse(
            json.dumps(response_dict),
            content_type='application/javascript')
    else:
        card_stats = []
        mod_fcstat = None
        std_fcstat = None
        formats = Format.cards.current_legal_formats(cards[0])
        card_format_details = {}
        for ff in formats:
            dets = {}
            card_format_details[ff.format] = dets
            dets['format'] = ff
            if ff.formatname == 'Standard':
                dets['format_abbr'] = 'Std'
                std_fcstat = FormatCardStat.objects.filter(physicalcard=cards[0].basecard.physicalcard, format=ff).first()
                card_stats.append(std_fcstat)
            elif ff.formatname == 'Modern':
                dets['format_abbr'] = 'Mod'
                mod_fcstat = FormatCardStat.objects.filter(physicalcard=cards[0].basecard.physicalcard, format=ff).first()
                card_stats.append(mod_fcstat)
            elif ff.formatname == 'TinyLeaders':
                dets['format_abbr'] = 'TL'
            elif ff.formatname == 'Commander':
                dets['format_abbr'] = 'EDH'
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
        similars = []
        for sim in cards[0].basecard.physicalcard.physicalcard.all().order_by('-score')[:18]:
            simcard = Card.objects.filter(basecard__physicalcard=sim.sim_physicalcard).order_by('-multiverseid').first()
            if simcard is not None:
                similars.append(simcard)
        response = render(request, 'cards/detail.html', {'request_muid': multiverseid,
                                                         'primary_basecard_id': primary_basecard_id,
                                                         'cards': card_list,
                                                         'keywords': cards[0].basecard.physicalcard.cardkeyword_set.all().order_by('-kwscore'),
                                                         'similars': similars,
                                                         'other_versions': twinCards,
                                                         'physicalCardTitle': " // ".join(card_titles),
                                                         'card_format_details': card_format_details,
                                                         'rulings': cards[0].basecard.get_rulings(),
                                                         'mod_card_stat': mod_fcstat,
                                                         'std_card_stat': std_fcstat,
                                                         'card_stats': card_stats,
                                                         #'rules_text_html': mark_safe(card.basecard.rules_text),
                                                         #'flavor_text_html': mark_safe(card.flavor_text),
                                                         #'mana_cost_html': mana_cost_html,
                                                         #'img_url': img_url, })
                                                         })
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

    # this is a BATTLE CHEAT so that you can battle a specific card
    if request.GET.get('muid', False) or request.session.get('battle_cont_muid', False) or request.GET.get('bcid', False):
        if request.GET.get('bcid', False):
            card_a = Card.objects.filter(basecard__id__exact=int(request.GET.get('bcid', 1))).order_by('-multiverseid').first()
        else:
            card_a = Card.objects.filter(multiverseid__exact=request.GET.get('muid', request.session.get('battle_cont_muid'))).first()
        first_card['basecard_id'] = card_a.basecard.id
        crsdb = CardRating.objects.filter(
            physicalcard=card_a.basecard.physicalcard,
            test__id__exact=test_id,
            format=format_obj)
        try:
            crdb = crsdb[0]
            first_card['mu'] = crdb.mu
            first_card['sigma'] = crdb.sigma
        except IndexError:
            # no op
            logger.error("Battle: bad ju-ju finding card ratings for basecard id " + str(card_a.basecard.id))
            pass
    else:
        fcsqls = 'SELECT fbc.basecard_id, cr.mu, cr.sigma, RAND() r FROM formatbasecard fbc JOIN basecard bc ON bc.id = fbc.basecard_id JOIN cardrating cr ON cr.physicalcard_id = bc.physicalcard_id JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE pc.layout IN %(layouts)s AND fbc.format_id = %(formatid)s ORDER BY r ASC LIMIT 1'
        #logger.error("First Card SQL: " + fcsqls)
        cursor.execute(fcsqls, params=query_params)
        rows = cursor.fetchall()
        first_card = {
            'basecard_id': rows[0][0],
            'mu': rows[0][1],
            'sigma': rows[0][2],
        }
        card_a = Card.objects.filter(basecard__id__exact=rows[0][0]).order_by('-multiverseid').first()

    query_params['cardabcid'] = first_card['basecard_id']
    while card_b is None:
        query_params['lowermu'] = first_card['mu'] - ((1 + find_iterations) * first_card['sigma'])
        query_params['uppermu'] = first_card['mu'] + ((1 + find_iterations) * first_card['sigma'])
        # now let's get a card of similar level - make it a real battle
        sqls = 'SELECT fbc.basecard_id, cr.mu, cr.sigma, RAND() r FROM formatbasecard fbc JOIN basecard bc ON bc.id = fbc.basecard_id JOIN cardrating cr ON cr.physicalcard_id = bc.physicalcard_id JOIN physicalcard AS pc ON bc.physicalcard_id = pc.id WHERE fbc.format_id = %(formatid)s AND fbc.basecard_id <> %(cardabcid)s AND cr.mu > %(lowermu)s AND cr.mu < %(uppermu)s AND pc.layout IN %(layouts)s ORDER BY r ASC LIMIT 1'
        #logger.error("Second Card SQL: " + sqls)
        cursor.execute(sqls, params=query_params)
        rows = cursor.fetchall()
        try:
            second_card = {
                'basecard_id': rows[0][0],
                'mu': rows[0][1],
                'sigma': rows[0][2],
            }
        except IndexError:
            logger.error("Battle iteration " + str(find_iterations) + ": UGH. IndexError. This SQL returned no result: " + sqls)
            logger.error("Battle: params were: " + str(query_params))
            # so let's just iterate this one again...
            find_iterations = find_iterations + 1
            continue

        #card_b_list = Card.objects.filter(basecard__id__exact=rows[1][0]).order_by('-multiverseid')
        card_b = Card.objects.filter(basecard__id__exact=second_card['basecard_id']).order_by('-multiverseid').first()

        # lastly, let's check to make sure that this battle has not already occured
        sqls = "SELECT 1 FROM battle WHERE session_key = '" + str(
            request.session.session_key) + "' AND ((winner_pcard_id = " + str(
            card_a.basecard.physicalcard.id) + " AND loser_pcard_id = " + str(
            card_b.basecard.physicalcard.id) + ") OR (winner_pcard_id = " + str(
                card_b.basecard.physicalcard.id) + " AND loser_pcard_id = " + str(
                    card_a.basecard.physicalcard.id) + "))"
        #'request.session.fbc.basecard_id, cr.mu, cr.sigma, RAND() r FROM formatbasecard fbc JOIN basecard bc ON bc.id = fbc.basecard_id JOIN cardrating cr ON cr.physicalcard_id = bc.physicalcard_id WHERE fbc.format_id = ' + str(format_id) + ' AND fbc.basecard_id <> ' + str(first_card['basecard_id']) + ' AND cr.mu > ' + str(first_card['mu'] - ((1 + find_iterations) * first_card['sigma'])) + ' AND cr.mu < ' + str(first_card['mu'] + ((1 + find_iterations) * first_card['sigma'])) + ' ORDER BY r ASC LIMIT 1'
        logger.error("Check battle SQL: " + sqls)
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
        logger.error(
            "Integrity Error on winning a battle... probably not a big deal: " +
            str(ie))

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
        logger.error(
            "updateRatings - could not get the CardRating for the winner. battle =" +
            str(battle))
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
        logger.error(
            "updateRatings - could not get the CardRating for the loser. battle =" +
            str(battle))
        return

    # calculate!
    logger.error("updating battles for cards " +
                 str(battle.winner_pcard.id) +
                 " and " +
                 str(battle.loser_pcard.id))
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
