# -*- coding: utf-8 -*-

from django.urls import path, re_path, include

from decks import views
from decks.views import TournamentListView

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^(?P<deck_id>[0-9]+)/$', views.deck, name='deck'),
    re_path(r'^cluster/(?P<cluster_id>[0-9]+)/$', views.cluster, name='cluster'),
    re_path(r'^cluster/(?P<cluster_id>[0-9]+)/cards/$', views.cluster_cards, name='cluster_cards'),
    re_path(r'^cluster/(?P<cluster_id>[0-9]+)/close/$', views.cluster_close, name='cluster_close'),
    re_path(r'^cluster/(?P<cluster_id>[0-9]+)/far/$', views.cluster_far, name='cluster_far'),
    re_path(r'^cluster/$', views.clusters, name='clusters'),
    re_path(r'^tournament/$', TournamentListView.as_view(), name='tournaments'),
    re_path(r'^tournament/(?P<tournament_id>[0-9]+)/$', views.tournament, name='tournament'),
    re_path(r'^crafter/$', views.recommendations, name='recommendations'),
    re_path(r'^manabase/$', views.manabaseanalysis, name='manabaseanalysis'),
]
