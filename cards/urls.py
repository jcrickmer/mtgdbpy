from django.conf.urls import patterns, url, include

from cards import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       # ex: /cards/_search
                       url(r'^_search$', views.search, name='search'),
                       url(r'^_ratings/$', views.ratings, name='ratings'),
                       url(r'^_ratings/(?P<format_id>[0-9]+)/$', views.ratings, name='ratings'),
                       url(r'^list/$', views.cardlist, name='list'),
                       url(r'^_list$', views.cardlist, name='list'),
                       # ex: /cards/5/
                       url(r'^(?P<multiverseid>\d+)/$', views.detail, name='detail'),
                       # ex: /cards/376251-augur-of-bolas/
                       url(r'^(?P<multiverseid>\d+)-(?P<slug>[a-zA-Z0-9-]+)/$', views.detail, name='detail'),
                       # ex: /cards/battle/
                       url(r'^battle/$', views.battle, name='battle'),
                       url(r'^battle/(?P<format>[a-zA-Z-]+)/$', views.battle, name='battle'),
                       url(r'^_winbattle$', views.winbattle, name='winbattle'),
                       # ex: /cards/augur-of-bolas/
                       url(r'^(?P<slug>[a-zA-Z-]+)/$', views.detail, name='detail'),
                       (r'^_textsearch/', include('haystack.urls')),
                       url(r'^_nameauto/', views.autocomplete, name='autocomplete'),
                       )
