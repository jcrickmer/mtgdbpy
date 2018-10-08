# -*- coding: utf-8 -*-

from django.urls import path, re_path, include

from cards import views
from cards import stub_views
from cards import utilviews

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^search/(?P<terms>[^/]+)/$', views.predefsearch, name='predefsearch'),
    # ex: /cards/_search
    re_path(r'^_search$', views.search, name='search'),
    re_path(r'^_ratings/$', views.ratings, name='ratings'),
    re_path(r'^_ratings/(?P<format_id>[0-9]+)/$', views.ratings, name='ratings'),
    re_path(r'^list/$', views.cardlist, name='list'),
    re_path(r'^_formats/$', views.formats, name='formats'),
    re_path(r'^_list$', views.cardlist, name='list'),
    re_path(r'^_similar_cards$', views.cardlist_sims, name='list_sims'),
    re_path(r'^_similar_cards/(?P<cardname>[^/]+)$', views.cardlist_sims, name='list_sims'),
    re_path(r'^_cardstats/(?P<formatname>[^/]+)/(?P<physicalcard_id>\d+)/$', views.cardstats, name='cardstats'),
    re_path(r'^_cardstats/(?P<formatname>[^/]+)/mvid-(?P<multiverseid>\d+)/$', views.cardstats, name='cardstats'),
    # format stats
    re_path(r'stats/(?P<formatname>[a-zA-Z-]+)/$', views.formatstats, name='formatstats'),
    # ex: /cards/5/
    re_path(r'^(?P<multiverseid>\d+)$', views.detail_by_multiverseid_noslash, name='detail_by_multiverseid_noslash'),
    re_path(r'^(?P<multiverseid>\d+)/$', views.detail_by_multiverseid, name='detail_by_multiverseid'),
    # ex: /cards/376251-augur-of-bolas/
    re_path(r'^(?P<multiverseid>\d+)-(?P<slug>[a-zA-Z0-9-]+)/$', views.detail, name='detail'),
    # ex: /cards/376251-augur-of-bolas/played-with/
    re_path(r'^(?P<multiverseid>\d+)-(?P<slug>[a-zA-Z0-9-]+)/(?P<formatname>[a-zA-Z0-9]+)-company/$', views.playedwith, name='playedwith'),
    # ex: /cards/battle/
    re_path(r'^battle/$', views.battle, name='battle'),
    re_path(r'^battle/(?P<format>[a-zA-Z-]+)/$', views.battle, name='battle'),
    re_path(r'^_winbattle$', views.winbattle, name='winbattle'),
    # ex: /cards/augur-of-bolas/
    re_path(r'^(?P<slug>[a-zA-Z-]+)/$', views.detail_by_slug, name='detail_by_slug'),
    re_path(r'^_nameauto/', views.autocomplete, name='autocomplete'),
    re_path(r'^_clustertest/(?P<test_id>[0-9]+)', utilviews.cardclustertest, name='cardclustertest'),
    re_path(r'^_clustertest/', utilviews.cardclustertest, name='cardclustertest'),
    re_path(r'^_cardpricetest/(?P<multiverseid>\S+)/?$', stub_views.card_price_ajax_stub, name='card_price_ajax_stub'),
    re_path(r'^_cardpricedbtest/(?P<multiverseid>\S+)/?$', stub_views.card_price_deckbox_ajax_stub, name='card_price_deckbox_ajax_stub'),
    re_path(r'^_ucp/$', views.update_card_price, name='update_card_price'),
    re_path(r'^_simstest/$', views.sims_test, name='sims_test'),

]
