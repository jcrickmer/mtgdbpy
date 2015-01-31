from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       url(r'^cards/admin/', include(admin.site.urls)),
                       url(r'^cards/',
                           include('cards.urls',
                                   namespace="cards")),
                       (r'^cn/(?P<path>.*)$',
                        'django.views.static.serve',
                        {'document_root': '/home/jason/projects/mtgdb/cn'}),
                       (r'^img/(?P<path>.*)$',
                        'django.views.static.serve',
                        {'document_root': '/home/jason/projects/mtgstats/card_images'}),
                       # Examples:
                       # url(r'^$', 'mtgdb.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^admin/', include(admin.site.urls)),
                       )
