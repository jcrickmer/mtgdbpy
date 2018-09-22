# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from cards import views
from cards import stub_views
from cards import utilviews

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/(?P<terms>[^/]+)/$', views.predefsearch, name='predefsearch'),
    # ex: /cards/_search
    url(r'^_search$', views.search, name='search'),
    url(r'^_ratings/$', views.ratings, name='ratings'),
    url(r'^_ratings/(?P<format_id>[0-9]+)/$', views.ratings, name='ratings'),
    url(r'^list/$', views.cardlist, name='list'),
    url(r'^_formats/$', views.formats, name='formats'),
    url(r'^_list$', views.cardlist, name='list'),
    url(r'^_similar_cards$', views.cardlist_sims, name='list_sims'),
    url(r'^_similar_cards/(?P<cardname>[^/]+)$', views.cardlist_sims, name='list_sims'),
    url(r'^_cardstats/(?P<formatname>[^/]+)/(?P<physicalcard_id>\d+)/$', views.cardstats, name='cardstats'),
    url(r'^_cardstats/(?P<formatname>[^/]+)/mvid-(?P<multiverseid>\d+)/$', views.cardstats, name='cardstats'),
    # format stats
    url(r'stats/(?P<formatname>[a-zA-Z-]+)/$', views.formatstats, name='formatstats'),
    # ex: /cards/5/
    url(r'^(?P<multiverseid>\d+)$', views.detail_by_multiverseid_noslash, name='detail_by_multiverseid_noslash'),
    url(r'^(?P<multiverseid>\d+)/$', views.detail_by_multiverseid, name='detail_by_multiverseid'),
    # ex: /cards/376251-augur-of-bolas/
    url(r'^(?P<multiverseid>\d+)-(?P<slug>[a-zA-Z0-9-]+)/$', views.detail, name='detail'),
    # ex: /cards/376251-augur-of-bolas/played-with/
    url(r'^(?P<multiverseid>\d+)-(?P<slug>[a-zA-Z0-9-]+)/(?P<formatname>[a-zA-Z0-9]+)-company/$', views.playedwith, name='playedwith'),
    # ex: /cards/battle/
    url(r'^battle/$', views.battle, name='battle'),
    url(r'^battle/(?P<format>[a-zA-Z-]+)/$', views.battle, name='battle'),
    url(r'^_winbattle$', views.winbattle, name='winbattle'),
    # ex: /cards/augur-of-bolas/
    url(r'^(?P<slug>[a-zA-Z-]+)/$', views.detail_by_slug, name='detail_by_slug'),
    url(r'^_nameauto/', views.autocomplete, name='autocomplete'),
    url(r'^_clustertest/(?P<test_id>[0-9]+)', utilviews.cardclustertest, name='cardclustertest'),
    url(r'^_clustertest/', utilviews.cardclustertest, name='cardclustertest'),
    url(r'^_cardpricetest/(?P<multiverseid>\S+)/?$', stub_views.card_price_ajax_stub, name='card_price_ajax_stub'),
    url(r'^_cardpricedbtest/(?P<multiverseid>\S+)/?$', stub_views.card_price_deckbox_ajax_stub, name='card_price_deckbox_ajax_stub'),
    url(r'^_ucp/$', views.update_card_price, name='update_card_price'),
    url(r'^_simstest/$', views.sims_test, name='sims_test'),

]
