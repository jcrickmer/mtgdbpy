from django.shortcuts import render
from decks.models import Deck, DeckCluster, DeckClusterDeck

import logging


def index(request):
    context = dict()
    return render(request, 'decks/index.html', context)


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
    farthest_decks = DeckClusterDeck.objects.filter(deckcluster=cluster).order_by('-distance')[0:3]
    context['decks'].append({'title': 'Farthest', 'decks': farthest_decks})
    return render(request, 'decks/cluster.html', context)
