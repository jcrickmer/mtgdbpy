from django.conf.urls import patterns, url

from mtgdbapp import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       # ex: /cards/5/
                       url(r'^(?P<multiverseid>\d+)/$', views.detail, name='detail'),
                       # ex: /polls/5/results/
                       url(r'^(?P<multiverseid>\d+)/results/$', views.results, name='results'),
                       # ex: /polls/5/vote/
                       url(r'^(?P<multiverseid>\d+)/vote/$', views.vote, name='vote'),
)
