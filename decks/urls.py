from django.conf.urls import patterns, url

from decks import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^cluster/(?P<cluster_id>[0-9]+)/$', views.cluster, name='cluster'),
                       url(r'^cluster/$', views.clusters, name='clusters'),
                       )
