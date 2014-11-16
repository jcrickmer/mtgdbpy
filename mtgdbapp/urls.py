from django.conf.urls import patterns, url

from mtgdbapp import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
					   # ex: /cards/_search
                       url(r'^_search$', views.search, name='search'),
                       url(r'^_list$', views.list, name='list'),
                       # ex: /cards/5/
                       url(r'^(?P<multiverseid>\d+)/$', views.detail, name='detail'),
                       # ex: /polls/results/
                       url(r'^list/$', views.list, name='list'),
                       # ex: /polls/5/vote/
                       url(r'^(?P<multiverseid>\d+)/vote/$', views.vote, name='vote'),
)
