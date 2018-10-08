# -*- coding: utf-8 -*-

from django.urls import path, include, re_path
from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from ajax_select import urls as ajax_select_urls

admin.autodiscover()

urlpatterns = [
    #re_path(r'^cards/admin/lookups/', include(ajax_select_urls)),
    #re_path(r'^cards/admin/', include(admin.site.urls)),
    re_path(r'^cards/', include(('cards.urls', 'cards'), namespace="cards")),
    re_path(r'^decks/', include(('decks.urls', 'decks'), namespace="decks")),
    re_path(r'^cn/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT_CN}),
    # this cn- URL is used to help refresh cache. If files in cn have changed,
    # updated base.html to include some new string to force cache flush
    # browser-side. Coresponds to an AliasMatch in the Apahce httpd.conf:
    # AliasMatch "^/cn-[0-9a-z]+/(.*)" "/opt/mtgdb-prod/cn/$1"
    re_path(r'^cn-[0-9a-z]+/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT_CN}),

    re_path(r'^fonts/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT_CN}),
    re_path(r'^img/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT_CARD_IMAGES}),
    re_path(r'^d/(?P<path>.*)$', serve, {'document_root': settings.DYNAMIC_IMAGE_FILE_ROOT}),
    # Examples:
    # url(r'^$', 'mtgdb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    path('admin/lookups/', include(ajax_select_urls)),
    path('admin/', admin.site.urls),
    re_path(r'^robots.txt$', serve, {'path': 'robots.txt', 'document_root': settings.STATIC_ROOT_CN}),
]
