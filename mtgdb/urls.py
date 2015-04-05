from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

from ajax_select import urls as ajax_select_urls

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^cards/admin/', include(admin.site.urls)),
                       url(r'^cards/', include('cards.urls', namespace="cards")),
                       url(r'^rules/', include('rules.urls', namespace="rules")),
                       url(r'^decks/', include('decks.urls', namespace="decks")),
                       (r'^cn/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT_CN}),
                       (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT_CARD_IMAGES}),
                       (r'^d/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.DYNAMIC_IMAGE_FILE_ROOT}),
                       # Examples:
                       # url(r'^$', 'mtgdb.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       (r'^admin/lookups/', include(ajax_select_urls)),
                       url(r'^admin/', include(admin.site.urls)),
                       )
