from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^cards/admin/', include(admin.site.urls)),
    url(r'^cards/', include('mtgdbapp.urls', namespace="cards")),
    (r'^cn/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/jason/projects/mtgdbpy/cn'}),
    (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/jason/projects/mtgstats/card_images'}),
)

