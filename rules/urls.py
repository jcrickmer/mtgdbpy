from django.conf.urls import url

from rules import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<section>.+)$', views.showsection, name='showsection'),
    #url(r'^(?P<path>.*)$', views.showdoc, name='showdoc'),
]
