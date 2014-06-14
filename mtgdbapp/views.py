from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from mtgdbapp.models import Card


def index(request):
    return search(request)


def search(request):
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


def list(request):
    card_list = Card.objects.order_by('multiverseid')[:500]
    paginator = Paginator(card_list, 25)
    page = request.GET.get('page')
    try:
        cards = paginator.page(page)
    except PageNotAnInteger:
        cards = paginator.page(1)
    except EmptyPage:
        cards = paginator.page(paginator.num_pages)

    context = {
        'cards': cards,
        }
    return render(request, 'cards/list.html', context)


def vote(request, multiverseid):
    return HttpResponse("You're voting on card %s." % multiverseid)
