from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from mtgdbapp.models import Card

def index(request):
    card_list = Card.objects.order_by('multiverseid')[:25]
    context = {
        'card_list': card_list,
        }
    return render(request, 'cards/index.html', context)

def detail(request, multiverseid):
    try:
        card = Card.objects.get(multiverseid=multiverseid)
    except Card.DoesNotExist:
        raise Http404
    return render(request, 'cards/detail.html', {'card': card})

def results(request, multiverseid):
    return HttpResponse("You're looking at the results of card %s." % multiverseid)

def vote(request, multiverseid):
    return HttpResponse("You're voting on card %s." % multiverseid)
