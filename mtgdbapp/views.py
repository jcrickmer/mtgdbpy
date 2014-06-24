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
	tag_open = '<img src="/cn/glyphs/clear.png" ' + base
	tag_close = '>'
	result = text; #.lower()
	result = result.replace("{w}", tag_open + 'class="magic-symbol-small symbol_mana_w_small" alt="{w}"' + tag_close)
	result = result.replace("{u}", tag_open + 'class="magic-symbol-small symbol_mana_u_small" alt="{u}"' + tag_close)
	result = result.replace("{b}", tag_open + 'class="magic-symbol-small symbol_mana_b_small" alt="{b}"' + tag_close)
	result = result.replace("{r}", tag_open + 'class="magic-symbol-small symbol_mana_r_small" alt="{r}"' + tag_close)
	result = result.replace("{g}", tag_open + 'class="magic-symbol-small symbol_mana_g_small" alt="{g}"' + tag_close)

	result = result.replace("{wp}", tag_open + 'class="magic-symbol-small symbol_mana_wp_small" alt="{wp}"' + tag_close)
	result = result.replace("{up}", tag_open + 'class="magic-symbol-small symbol_mana_up_small" alt="{up}"' + tag_close)
	result = result.replace("{bp}", tag_open + 'class="magic-symbol-small symbol_mana_bp_small" alt="{bp}"' + tag_close)
	result = result.replace("{rp}", tag_open + 'class="magic-symbol-small symbol_mana_rp_small" alt="{rp}"' + tag_close)
	result = result.replace("{gp}", tag_open + 'class="magic-symbol-small symbol_mana_gp_small" alt="{gp}"' + tag_close)

	result = result.replace("{2w}", tag_open + 'class="magic-symbol-small symbol_mana_2w_small" alt="{2w}"' + tag_close)
	result = result.replace("{2u}", tag_open + 'class="magic-symbol-small symbol_mana_2u_small" alt="{2u}"' + tag_close)
	result = result.replace("{2b}", tag_open + 'class="magic-symbol-small symbol_mana_2b_small" alt="{2b}"' + tag_close)
	result = result.replace("{2r}", tag_open + 'class="magic-symbol-small symbol_mana_2r_small" alt="{2r}"' + tag_close)
	result = result.replace("{2g}", tag_open + 'class="magic-symbol-small symbol_mana_2g_small" alt="{2g}"' + tag_close)

	result = result.replace("{wu}", tag_open + 'class="magic-symbol-small symbol_mana_wu_small" alt="{wu}"' + tag_close)
	result = result.replace("{wb}", tag_open + 'class="magic-symbol-small symbol_mana_wb_small" alt="{wb}"' + tag_close)
	result = result.replace("{ub}", tag_open + 'class="magic-symbol-small symbol_mana_ub_small" alt="{ub}"' + tag_close)
	result = result.replace("{ur}", tag_open + 'class="magic-symbol-small symbol_mana_ur_small" alt="{ur}"' + tag_close)
	result = result.replace("{br}", tag_open + 'class="magic-symbol-small symbol_mana_br_small" alt="{br}"' + tag_close)

	result = result.replace("{bg}", tag_open + 'class="magic-symbol-small symbol_mana_bg_small" alt="{bg}"' + tag_close)
	result = result.replace("{rg}", tag_open + 'class="magic-symbol-small symbol_mana_rg_small" alt="{rg}"' + tag_close)
	result = result.replace("{rw}", tag_open + 'class="magic-symbol-small symbol_mana_rw_small" alt="{rw}"' + tag_close)
	result = result.replace("{gw}", tag_open + 'class="magic-symbol-small symbol_mana_gw_small" alt="{gw}"' + tag_close)
	result = result.replace("{gu}", tag_open + 'class="magic-symbol-small symbol_mana_gu_small" alt="{gu}"' + tag_close)

	result = result.replace("{x}", tag_open + 'class="magic-symbol-small symbol_mana_x_small" alt="{x}"' + tag_close)
	result = result.replace("{p}", tag_open + 'class="magic-symbol-small symbol_phyrexian_small" alt="{p}"' + tag_close)
	result = result.replace("{t}", tag_open + 'class="magic-symbol-small symbol_tap_small" alt="{t}"' + tag_close)
	result = result.replace("{q}", tag_open + 'class="magic-symbol-small symbol_untap_small" alt="{q}"' + tag_close)
	result = result.replace("{untap}", tag_open + 'class="magic-symbol-small symbol_untap_small" alt="{q}"' + tag_close)

	# ####
	result = result.replace("{W}", tag_open + 'class="magic-symbol-small symbol_mana_w_small" alt="{w}"' + tag_close)
	result = result.replace("{U}", tag_open + 'class="magic-symbol-small symbol_mana_u_small" alt="{u}"' + tag_close)
	result = result.replace("{B}", tag_open + 'class="magic-symbol-small symbol_mana_b_small" alt="{b}"' + tag_close)
	result = result.replace("{R}", tag_open + 'class="magic-symbol-small symbol_mana_r_small" alt="{r}"' + tag_close)
	result = result.replace("{G}", tag_open + 'class="magic-symbol-small symbol_mana_g_small" alt="{g}"' + tag_close)

	result = result.replace("{WP}", tag_open + 'class="magic-symbol-small symbol_mana_wp_small" alt="{wp}"' + tag_close)
	result = result.replace("{UP}", tag_open + 'class="magic-symbol-small symbol_mana_up_small" alt="{up}"' + tag_close)
	result = result.replace("{BP}", tag_open + 'class="magic-symbol-small symbol_mana_bp_small" alt="{bp}"' + tag_close)
	result = result.replace("{RP}", tag_open + 'class="magic-symbol-small symbol_mana_rp_small" alt="{rp}"' + tag_close)
	result = result.replace("{GP}", tag_open + 'class="magic-symbol-small symbol_mana_gp_small" alt="{gp}"' + tag_close)

	result = result.replace("{2W}", tag_open + 'class="magic-symbol-small symbol_mana_2w_small" alt="{2w}"' + tag_close)
	result = result.replace("{2U}", tag_open + 'class="magic-symbol-small symbol_mana_2u_small" alt="{2u}"' + tag_close)
	result = result.replace("{2B}", tag_open + 'class="magic-symbol-small symbol_mana_2b_small" alt="{2b}"' + tag_close)
	result = result.replace("{2R}", tag_open + 'class="magic-symbol-small symbol_mana_2r_small" alt="{2r}"' + tag_close)
	result = result.replace("{2G}", tag_open + 'class="magic-symbol-small symbol_mana_2g_small" alt="{2g}"' + tag_close)

	result = result.replace("{WU}", tag_open + 'class="magic-symbol-small symbol_mana_wu_small" alt="{wu}"' + tag_close)
	result = result.replace("{WB}", tag_open + 'class="magic-symbol-small symbol_mana_wb_small" alt="{wb}"' + tag_close)
	result = result.replace("{UB}", tag_open + 'class="magic-symbol-small symbol_mana_ub_small" alt="{ub}"' + tag_close)
	result = result.replace("{UR}", tag_open + 'class="magic-symbol-small symbol_mana_ur_small" alt="{ur}"' + tag_close)
	result = result.replace("{BR}", tag_open + 'class="magic-symbol-small symbol_mana_br_small" alt="{br}"' + tag_close)
	result = result.replace("{BG}", tag_open + 'class="magic-symbol-small symbol_mana_bg_small" alt="{bg}"' + tag_close)
	result = result.replace("{RG}", tag_open + 'class="magic-symbol-small symbol_mana_rg_small" alt="{rg}"' + tag_close)
	result = result.replace("{RW}", tag_open + 'class="magic-symbol-small symbol_mana_rw_small" alt="{rw}"' + tag_close)
	result = result.replace("{GW}", tag_open + 'class="magic-symbol-small symbol_mana_gw_small" alt="{gw}"' + tag_close)
	result = result.replace("{GU}", tag_open + 'class="magic-symbol-small symbol_mana_gu_small" alt="{gu}"' + tag_close)

	result = result.replace("{X}", tag_open + 'class="magic-symbol-small symbol_mana_x_small" alt="{x}"' + tag_close)
	result = result.replace("{P}", tag_open + 'class="magic-symbol-small symbol_mana_phyrexian_small" alt="{p}"' + tag_close)
	result = result.replace("{T}", tag_open + 'class="magic-symbol-small symbol_tap_small" alt="{t}"' + tag_close)
	result = result.replace("{Q}", tag_open + 'class="magic-symbol-small symbol_untap_small" alt="{q}"' + tag_close)
	result = result.replace("{UNTAP}", tag_open + 'class="magic-symbol-small symbol_untap_small" alt="{q}"' + tag_close)
	# ####

	for x in range(0, 15):
		result = result.replace("{" + str(x) + "}", tag_open + ' class="magic-symbol-small symbol_mana_' + str(x) + '_small" alt="{' + str(x) + '}"' + tag_close)

	result = result.replace("\n", "<br />\n")

	return mark_safe(result)

def detail(request, multiverseid):
	try:
		cards = Card.objects.filter(multiverseid=multiverseid).order_by('card_number')
	except Card.DoesNotExist:
		raise Http404
	backCards = []
	if len(cards) > 0:
		logger = logging.getLogger(__name__)
		backCards = Card.objects.filter(basecard__physicalcard__id = cards[0].basecard.physicalcard.id, expansionset__id = cards[0].expansionset.id)
		logger.error(backCards)
	cards = cards | backCards
	twinCards = Card.objects.filter(basecard__id = cards[0].basecard.id).order_by('multiverseid')
	response = HttpResponse("Lame. Something must be broken.")
	jcards = []
	card_list = []
	card_titles = []
	for card in cards:
		card_helper = {}
		mana_cost_html = convertSymbolsToHTML(card.basecard.mana_cost)
		#img_url = 'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=' + str(card.multiverseid) + '&type=card'
		card_helper['img_url'] = '/img/' + str(card.multiverseid) + '.jpg'
		card_helper['mana_cost_html'] = mark_safe(mana_cost_html)
		card_helper['rules_text_html'] = mark_safe(convertSymbolsToHTML(card.basecard.rules_text))
		card_helper['flavor_text_html'] = mark_safe(card.flavor_text)
		card_titles.append(card.basecard.name)
		
		if request.is_ajax():
			response_dict = {}
			jcard = {'name': card.basecard.name,
					 'mana_cost': card.basecard.mana_cost,
					 'mana_cost_html': mana_cost_html,
					 'type': [tt.type for tt in card.basecard.types.all()],
					 'subtype': [st.subtype for st in card.basecard.subtypes.all()],
					 'text': card_helper['rules_text_html'],
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
		response_dict.update({'status': 'success', 'physicalCardTitle': " // ".join(card_titles), 'cards': jcards, })
		response = HttpResponse(json.dumps(response_dict), mimetype='application/javascript')
	else:
		response = render(request, 'cards/detail.html', {'cards': card_list,
														 'other_versions': twinCards,
														 'physicalCardTitle': " // ".join(card_titles),
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
