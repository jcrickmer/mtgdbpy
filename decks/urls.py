from django.conf.urls import patterns, url

from decks import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^cluster/(?P<cluster_id>[0-9]+)/$', views.cluster, name='cluster'),
                       url(r'^cluster/(?P<cluster_id>[0-9]+)/cards/$', views.cluster_cards, name='cluster_cards'),
                       url(r'^cluster/(?P<cluster_id>[0-9]+)/close/$', views.cluster_close, name='cluster_close'),
                       url(r'^cluster/(?P<cluster_id>[0-9]+)/far/$', views.cluster_far, name='cluster_far'),
                       url(r'^cluster/$', views.clusters, name='clusters'),
                       )
