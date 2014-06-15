from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^cards/admin/', include(admin.site.urls)),
    url(r'^cards/', include('mtgdbapp.urls', namespace="cards")),
)
