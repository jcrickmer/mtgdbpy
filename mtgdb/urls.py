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
    # this cn- URL is used to help refresh cache. If files in cn have changed, updated base.html to include some new string to force cache flush browser-side. Coresponds to an AliasMatch in the Apahce httpd.conf:  AliasMatch "^/cn-[0-9a-z]+/(.*)" "/opt/mtgdb-prod/cn/$1"
    url(r'^cn-[0-9a-z]+/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT_CN}),
    
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
