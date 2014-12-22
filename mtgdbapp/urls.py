from django.conf.urls import patterns, url

from mtgdbapp import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
					   # ex: /cards/_search
                       url(r'^_search$', views.search, name='search'),
                       url(r'^ratings/$', views.ratings, name='ratings'),
                       url(r'^list/$', views.list, name='list'),
                       url(r'^_list$', views.list, name='list'),
                       # ex: /cards/5/
                       url(r'^(?P<multiverseid>\d+)/$', views.detail, name='detail'),
					   # ex: /cards/376251-augur-of-bolas/
                       url(r'^(?P<multiverseid>\d+)-(?P<slug>[a-zA-Z-]+)/$', views.detail, name='detail'),
					   # ex: /cards/battle/
					   url(r'^battle/$', views.battle, name='battle'),
					   url(r'^battle/(?P<format>[a-zA-Z-]+)/$', views.battle, name='battle'),
					   url(r'^_winbattle$', views.winbattle, name='winbattle'),
					   # ex: /cards/augur-of-bolas/
                       url(r'^(?P<slug>[a-zA-Z-]+)/$', views.detail, name='detail'),
                       # ex: /polls/results/
                       # ex: /polls/5/vote/
                       url(r'^(?P<multiverseid>\d+)/vote/$', views.vote, name='vote'),
)
