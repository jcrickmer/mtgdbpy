from django.conf.urls import patterns, url

from decks import views
from decks.views import TournamentListView

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^(?P<deck_id>[0-9]+)/$', views.deck, name='deck'),
                       url(r'^cluster/(?P<cluster_id>[0-9]+)/$', views.cluster, name='cluster'),
                       url(r'^cluster/(?P<cluster_id>[0-9]+)/cards/$', views.cluster_cards, name='cluster_cards'),
                       url(r'^cluster/(?P<cluster_id>[0-9]+)/close/$', views.cluster_close, name='cluster_close'),
                       url(r'^cluster/(?P<cluster_id>[0-9]+)/far/$', views.cluster_far, name='cluster_far'),
                       url(r'^cluster/$', views.clusters, name='clusters'),
                       url(r'^tournament/$', TournamentListView.as_view(), name='tournaments'),
                       url(r'^tournament/(?P<tournament_id>[0-9]+)/$', views.tournament, name='tournament'),
                       )
