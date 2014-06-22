from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.db.models import Max, Min

from mtgdbapp.models import Card

# import the logging library
import logging


def index(request):
    return search(request)


def search(request):
    card_list = Card.objects.order_by('multiverseid')[:25]
    context = {
        'card_list': card_list,
        }
    return render(request, 'cards/index.html', context)


def convertSymbolsToHTML(text):
	base = '/cn/glyphs/'
	tag_open = '<img class="magic-symbol" src="' + base
	tag_close = '>'
	result = text.replace("{w}", tag_open + 'symbol_mana_w_small.gif" alt="{w}"' + tag_close)
	result = result.replace("{u}", tag_open + 'symbol_mana_u_small.gif" alt="{u}"' + tag_close)
	result = result.replace("{b}", tag_open + 'symbol_mana_b_small.gif" alt="{b}"' + tag_close)
	result = result.replace("{r}", tag_open + 'symbol_mana_r_small.gif" alt="{r}"' + tag_close)
	result = result.replace("{g}", tag_open + 'symbol_mana_g_small.gif" alt="{g}"' + tag_close)
	for x in range(0, 15):
		result = result.replace("{" + str(x) + "}", tag_open + 'symbol_mana_' + str(x) + '_small.gif" alt="{' + str(x) + '}"' + tag_close)
	return mark_safe(result)

def detail(request, multiverseid):
	try:
		cards = Card.objects.filter(multiverseid=multiverseid).order_by('card_number')
	except Card.DoesNotExist:
		raise Http404
	twinCards = Card.objects.filter(basecard__id = cards[0].basecard.id).order_by('multiverseid')
	response = HttpResponse("stupid")
	jcards = []
	card_list = []
	for card in cards:
		card_helper = {}
		mana_cost_html = convertSymbolsToHTML(card.basecard.mana_cost)
		#img_url = 'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=' + str(card.multiverseid) + '&type=card'
		card_helper['img_url'] = '/img/' + str(card.multiverseid) + '.jpg'
		card_helper['mana_cost_html'] = mark_safe(mana_cost_html)
		card_helper['rules_text_html'] = mark_safe(card.basecard.rules_text)
		card_helper['flavor_text_html'] = mark_safe(card.flavor_text)
		
		if request.is_ajax():
			response_dict = {}
			jcard = {'name': card.basecard.name,
					 'mana_cost': card.basecard.mana_cost,
					 'mana_cost_html': mana_cost_html,
			         'type': [tt.type for tt in card.basecard.types.all()],
			         'subtype': [st.subtype for st in card.basecard.subtypes.all()],
				     'text': card.basecard.rules_text,
				     'flavor_text': card.flavor_text,
				     'mark': '' if card.mark is None else card.mark.mark,
				     'cmc': card.basecard.cmc,
				     'multiverseid': card.multiverseid,
				     'expansionset': {'name': card.expansionset.name, 'abbr':card.expansionset.abbr},
				     'rarity': card.rarity.rarity,
				     'card_number': card.card_number,
				     'img_url': card_helper['img_url'],
				     'power': card.basecard.power,
				     'toughness': card.basecard.toughness,
				     'loyalty': card.basecard.loyalty,
				     'colors': [cc.color for cc in card.basecard.colors.all()]
				 }
			jcards.append(jcard)
		card_list.append({'card': card, 'helper': card_helper})

	if request.is_ajax():
		response_dict.update({'status': 'success', 'cards': jcards, })
		response = HttpResponse(json.dumps(response_dict), mimetype='application/javascript')
	else:
		response = render(request, 'cards/detail.html', {'cards': card_list,
														 'other_versions': twinCards,
														 #'rules_text_html': mark_safe(card.basecard.rules_text),
														 #'flavor_text_html': mark_safe(card.flavor_text),
														 #'mana_cost_html': mana_cost_html,
														 #'img_url': img_url, })
														 })
	return response

def list(request):
	card_list = {}
	# Let's see if the user is trying to perform a search. Any value here will do.
	if request.GET.get('search'):
		# must be trying to search. Let's figure out what they want and add that term to their session.
		request.session['qcardname'] = request.GET['qcardname']

	# Ok, lets get the data. First, if they are querying by card name, let's get that list.
	if request.session.get('qcardname', False):
		# Not sure of the performance in here. Basically, I needed to
		# do a GROUP BY to get the max multiverseid and only display
		# that card. The first query here is getting the max
		# multiverseid for the given query. The second query then uses
		# that "mid_max" value to get back a list of all of the cards.
		card_listP = Card.objects.filter(basecard__name__icontains = request.session.get('qcardname', '')).values('basecard__id').annotate(mid_max=Max('multiverseid'))
		card_list = Card.objects.filter(multiverseid__in=[g['mid_max'] for g in card_listP]).order_by('basecard__name')

	else:
		# Nope? They must just want everything. Too big, though - let's constrain it to 500 records.
		card_listP = Card.objects.values('basecard__id').annotate(mid_max=Max('multiverseid'))[:500]
		card_list = Card.objects.filter(multiverseid__in=[g['mid_max'] for g in card_listP]).order_by('basecard__name')

	# Get an instance of a logger
	#logger = logging.getLogger(__name__)
	#logger.error(card_list)
	
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
