from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import simplejson

from mtgdbapp.models import Card


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
		card = Card.objects.get(multiverseid=multiverseid)
	except Card.DoesNotExist:
		raise Http404
	mana_cost_html = convertSymbolsToHTML(card.basecard.mana_cost)
	img_url = 'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=' + str(card.multiverseid) + '&type=card'
	response = HttpResponse("stupid")
	if request.is_ajax():
		response_dict = {}
		jcard = {'name': card.basecard.name,
				 'mana_cost': card.basecard.mana_cost,
				 'mana_cost_html': mana_cost_html,
				 #'type': ' '.join(card.basecard.types.all),
				 #'subtype': ' '.join(card.basecard.subtypes.all),
				 'text': card.basecard.rules_text,
				 'flavor_text': card.flavor_text,
				 #'mark': card.mark.mark,
				 'cmc': card.basecard.cmc,
				 'multiverseid': card.multiverseid,
				 'expansionset': {'name': card.expansionset.name, 'abbr':card.expansionset.abbr},
				 'rarity': card.rarity.rarity,
				 'card_number': card.card_number,
				 'img_url': img_url,
				 }

# 				 'color': join(",  <td>{% for tcolor in card.basecard.colors.all %}{{ tcolor.color }} {% endfor %}{% if card.basecard.colors.all|length == 0 %}Colorless{% endif %}
# {% if card.basecard.power %}
#       <td>Power<td>
#       <td>{{ card.basecard.power }}</td>
# {% endif %}
# {% if card.basecard.toughness %}
#       <td>Toughness<td>
#       <td>{{ card.basecard.toughness }}</td>
# {% endif %}
# {% if card.basecard.loyalty > 0 %}
#       <td>Loyalty<td>
#       <td>{{ card.basecard.loyalty }}</td>
# {% endif %}

		response_dict.update({'status': 'success', 'card': jcard, })
		response = HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
	else:
		response = render(request, 'cards/detail.html', {'card': card,
														 'rules_text_html': mark_safe(card.basecard.rules_text),
														 'flavor_text_html': mark_safe(card.flavor_text),
														 'mana_cost_html': mana_cost_html,
														 'img_url': img_url, })
	return response

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