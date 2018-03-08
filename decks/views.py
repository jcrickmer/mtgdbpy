# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from decks.models import Deck, DeckCluster, DeckClusterDeck, Tournament, TournamentDeck, Recommender, Analyzer, DeckCard
from cards.models import PhysicalCard, Format, Supertype, FormatBasecard
from django.http import Http404
from django.views.generic import ListView
import logging
from django.core.cache import cache
from django.db.models import Max, Min, Count, Sum, Avg
from django.conf import settings
from datetime import datetime, timedelta
import sys
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import smart_text

BASE_CONTEXT = {'settings': {
    'HOME_URL': settings.HOME_URL,
    'DECKBOX_URL': settings.DECKBOX_URL,
    'DECKBOX_LOGIN_URL': settings.DECKBOX_LOGIN_URL,
    'DECKBOX_PRICE_URL_BASE': settings.DECKBOX_PRICE_URL_BASE,
    'GA_TRACKING_ID': settings.GA_TRACKING_ID,
    'GTM_ID': settings.GTM_ID,
}
}


def index(request):
    context = BASE_CONTEXT.copy()
    return render(request, 'decks/index.html', context)


def deck(request, deck_id=None):
    deck = None
    try:
        deck = Deck.objects.get(pk=deck_id)
    except Deck.DoesNotExist:
        raise Http404
    context = BASE_CONTEXT.copy()
    context['deck'] = deck
    context['cdeck'] = dict()
    context['cdeck']['deck'] = deck
    return render(request, 'decks/deck.html', context)


def clusters(request):
    context = BASE_CONTEXT.copy()
    clusters = DeckCluster.objects.all()
    context['clusters'] = clusters
    return render(request, 'decks/clusters.html', context)


def cluster(request, cluster_id=None):
    logger = logging.getLogger(__name__)
    cluster = None
    try:
        cluster = DeckCluster.objects.get(pk=cluster_id)
    except DeckCluster.DoesNotExist:
        raise Http404

    context = BASE_CONTEXT.copy()
    context['cluster'] = cluster
    context['decks'] = list()
    closest_decks = DeckClusterDeck.objects.filter(deckcluster=cluster).order_by('distance')[0:3]
    context['decks'].append({'title': 'Closest', 'decks': closest_decks})
    #farthest_decks = DeckClusterDeck.objects.filter(deckcluster=cluster).order_by('-distance')[0:3]
    #context['decks'].append({'title': 'Farthest', 'decks': farthest_decks})
    return render(request, 'decks/cluster.html', context)


def cluster_list(request, cluster_id=None, order='distance'):
    logger = logging.getLogger(__name__)
    cluster = None
    try:
        cluster = DeckCluster.objects.get(pk=cluster_id)
    except DeckCluster.DoesNotExist:
        raise Http404

    context = BASE_CONTEXT.copy()
    context['cluster'] = cluster
    context['decks'] = list()
    decks = DeckClusterDeck.objects.filter(deckcluster=cluster).order_by(order)[0:5]
    block = 'Closest'
    if order == '-distance':
        block = 'Farthest'
    context['decks'].append({'title': block, 'decks': decks})
    return render(request, 'decks/cluster_list.html', context)


def cluster_close(request, cluster_id=None):
    return cluster_list(request, cluster_id, 'distance')


def cluster_far(request, cluster_id=None):
    return cluster_list(request, cluster_id, '-distance')


def cluster_cards(request, cluster_id=None):
    logger = logging.getLogger(__name__)
    cluster = None
    try:
        cluster = DeckCluster.objects.get(pk=cluster_id)
    except DeckCluster.DoesNotExist:
        raise Http404

    context = BASE_CONTEXT.copy()
    context['cluster'] = cluster

    cards_sql = '''SELECT dc.physicalcard_id as id, SUM(dc.cardcount) as card_count, COUNT(dcdm.deck_id) AS deck_main_count, COUNT(dcds.deck_id) AS deck_side_count, AVG(dc.cardcount) AS card_average FROM deckcard AS dc LEFT JOIN deck dmain ON dc.deck_id = dmain.id LEFT JOIN deckclusterdeck dcdm ON dcdm.deck_id = dmain.id AND dc.board = 'MAIN' AND dcdm.deckcluster_id = %s LEFT JOIN deck dside ON dc.deck_id = dside.id LEFT JOIN deckclusterdeck dcds ON dcds.deck_id = dside.id AND dc.board = 'SIDE' AND dcds.deckcluster_id = %s WHERE (dcdm.deckcluster_id = %s OR dcdm.deckcluster_id IS NULL) AND (dcds.deckcluster_id = %s OR dcds.deckcluster_id IS NULL) AND (dcdm.deckcluster_id IS NOT NULL OR dcds.deckcluster_id IS NOT NULL) GROUP BY dc.physicalcard_id ORDER BY card_count DESC'''
    pcards = cache.get('cluster_cards-' + str(cluster_id))
    if pcards is None:
        pcards = PhysicalCard.objects.raw(cards_sql, [cluster_id, cluster_id, cluster_id, cluster_id])
        cache.set('cluster_cards-' + str(cluster_id), pcards, 300)

    context['physicalcards'] = pcards

    return render(request, 'decks/cluster_cards.html', context)


def tournament(request, tournament_id=None):
    tournament = None
    try:
        tournament = Tournament.objects.get(pk=tournament_id)
    except Tournament.DoesNotExist:
        raise Http404

    context = BASE_CONTEXT.copy()
    context['tournament'] = tournament
    tdecks = TournamentDeck.objects.filter(tournament=tournament).order_by('place')
    context['tournament_decks'] = tdecks
    return render(request, 'decks/tournament.html', context)


class TournamentListView(ListView):
    model = Tournament
    template_name = 'decks/tournaments.html'
    context_object_name = 'tournament_list'
    queryset = Tournament.objects.filter(format__formatname='Modern').annotate(deck_count=Count('tournamentdeck')).order_by('-start_date')
    paginate_by = 25


def recommendations(request):
    context = BASE_CONTEXT.copy()
    context['current_formats'] = Format.objects.filter(start_date__lte=datetime.today(),
                                                       end_date__gte=datetime.today()).order_by('format')
    # REVISIT - unsafe index
    context['format'] = context['current_formats'][0]

    include_lands = 'exclude_lands' not in request.POST
    context['exclude_lands'] = not include_lands

    pcs = list()
    if 'format' in request.POST:
        for ff in context['current_formats']:
            if request.POST['format'] == ff.format:
                context['format'] = ff
                break
    if 'cardlist' in request.POST:
        try:
            pcs_dict = Deck.read_cards_from_text(request.POST['cardlist'], throw_exception=False)
            for key in pcs_dict:
                if key != 'errors' and 'physicalcard' in pcs_dict[key]:
                    pcs.append(pcs_dict['physicalcard'])
        except Deck.CardsNotFoundException as cnfe:
            pass
        #sys.stderr.write("cardlist is '{}'".format(pcs))
    context['card_list'] = (a.get_card_name() for a in pcs)
    context['seeds'] = (a.get_latest_card() for a in pcs)
    context['recommendations'] = ()
    context['spicy'] = list()
    if len(pcs):
        dcr = Recommender()
        context['recommendations'] = dcr.get_recommended_cards(pcs, context['format'], include_lands=include_lands)

        # get spicy...
        basic_supertype = Supertype.objects.filter(supertype='Basic').first()
        #sys.stderr.write("Basic type is {}\n".format(basic_supertype))
        for tcard in context['recommendations']:
            if basic_supertype in tcard.basecard.types.all():
                # Let's not look up similar cards to Basic lands
                continue

            sims = tcard.basecard.physicalcard.find_similar_cards(max_results=4)
            for sim in sims:
                #sys.stderr.write("%%%% SIM IS {} for {}\n".format(sim, tcard))
                if sim.basecard.physicalcard in pcs:
                    #sys.stderr.write("-- skipping {} for spicy because the user already wants it!\n".format(sim))
                    continue
                # Let's not consider Basic lands as spicy
                if basic_supertype in sim.basecard.supertypes.all():
                    #sys.stderr.write("-- skipping basic land for spicy.\n")
                    continue
                # Let's only recommend cards in the current format
                if FormatBasecard.objects.filter(basecard=sim.basecard, format=context['format']).count() == 0:
                    #sys.stderr.write("-- skipping {} for spicy because it isn't in format.\n".format(sim))
                    continue
                if sim in context['recommendations']:
                    #sys.stderr.write("-- skipping {} for spicy because it is already recommended.\n".format(sim))
                    continue
                if sim in context['spicy']:
                    #sys.stderr.write("-- skipping {} for spicy because it is already spicy!\n".format(sim))
                    continue
                #sys.stderr.write("starting with score of {}\n".format(tcard.annotations['match_confidence']))
                sim.annotations['spicy_score'] = tcard.annotations['match_confidence'] + (sim.annotations['similarity_score'] * 50.0)
                context['spicy'].append(sim)
                break
            if len(context['spicy']) >= 8:
                break
    return render(request, 'decks/recommendations.html', context)


def manabaseanalysis(request):
    context = BASE_CONTEXT.copy()

    context['current_formats'] = Format.objects.filter(start_date__lte=datetime.today(),
                                                       end_date__gte=datetime.today()).order_by('format')
    # REVISIT - unsafe index
    context['format'] = context['current_formats'][0]

    card_list = '''1 Pithing Needle
4 Chromatic Star
1 Ancient Grudge
1 Boil
3 Nature's Claim
3 Pyroclasm
4 Expedition Map
3 Oblivion Stone
4 Sylvan Scrying
4 Ancient Stirrings
1 Relic of Progenitus
4 Wurmcoil Engine
3 Thragtusk
4 Chromatic Sphere
4 Karn Liberated
1 Grafdigger's Cage
2 Ugin, the Spirit Dragon
2 Ulamog, the Ceaseless Hunger
2 Warping Wail
1 Kozilek's Return
1 World Breaker'''

    if 'format' in request.POST:
        for ff in context['current_formats']:
            if request.POST['format'] == ff.format:
                context['format'] = ff
                break
    if 'cardlist' in request.POST:
        card_list = request.POST['cardlist']
    deck_cards = Deck.read_cards_from_text(card_list, throw_exception=False)

    if 'errors' in deck_cards:
        context['errors'] = deck_cards['errors']
    context['card_list'] = list()
    for key in deck_cards:
        if key != 'errors' and isinstance(deck_cards[key], dict) and 'physicalcard' in deck_cards[key]:
            context['card_list'].append('{} {}'.format(deck_cards[key]['card_count'], deck_cards[key]['physicalcard'].get_card_name()))

    analyzer = Analyzer(format=context['format'])
    deck_score_tuples, query = analyzer.analyze(deck_cards)
    context['analysis'] = query
    context['analysis_json'] = json.dumps(query, sort_keys=True, indent=2, cls=DjangoJSONEncoder)
    context['deckcards'] = list()
    if len(deck_score_tuples):
        all_deckcards = DeckCard.objects.filter(deck=deck_score_tuples[0][0])
        context['recommendation_score'] = 1000.0 - deck_score_tuples[0][1]
        for dc in all_deckcards:
            if dc.physicalcard.get_face_basecard().is_land():
                context['deckcards'].append(dc)
    return render(request, 'decks/manabase.html', context)
