# -*- coding: utf-8 -*-
from django.shortcuts import render
from decks.models import Deck, DeckCluster, DeckClusterDeck, Tournament, TournamentDeck
from cards.models import PhysicalCard
from django.views.generic import ListView
import logging
from django.core.cache import cache
from django.db.models import Max, Min, Count, Sum, Avg

def index(request):
    context = dict()
    return render(request, 'decks/index.html', context)


def deck(request, deck_id=None):
    deck = None
    try:
        deck = Deck.objects.get(pk=deck_id)
    except Deck.DoesNotExist:
        raise Http404
    context = dict()
    context['deck'] = deck
    context['cdeck'] = dict()
    context['cdeck']['deck'] = deck
    return render(request, 'decks/deck.html', context)
        
def clusters(request):
    context = dict()
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

    context = dict()
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

    context = dict()
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

    context = dict()
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

    context = dict()
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
    
