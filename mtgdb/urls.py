# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from ajax_select import urls as ajax_select_urls

admin.autodiscover()

urlpatterns = [
    url(r'^cards/admin/lookups/', include(ajax_select_urls)),
    url(r'^cards/admin/', include(admin.site.urls)),
    url(r'^cards/', include('cards.urls', namespace="cards")),
    url(r'^decks/', include('decks.urls', namespace="decks")),
    url(r'^cn/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT_CN}),
    url(r'^fonts/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT_CN}),
    url(r'^img/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT_CARD_IMAGES}),
    url(r'^d/(?P<path>.*)$', serve, {'document_root': settings.DYNAMIC_IMAGE_FILE_ROOT}),
    # Examples:
    # url(r'^$', 'mtgdb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots.txt$', serve, {'path': 'robots.txt', 'document_root': settings.STATIC_ROOT_CN}),
]
