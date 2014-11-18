from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.db.models import Max, Min
from django.shortcuts import redirect

from mtgdbapp.models import Card
from mtgdbapp.models import Type
from mtgdbapp.models import Subtype

import json

# import the logging library
import logging

#
# The index view simple shows a search page. The page may be
# interactive, but the index view has no specific interactions
#
# From the index template's search interface, the user may
# "search", which uses the search method. This method removes all search
#  query terms from the sessions, and then sets the new ones based on
# what you entered. With search terms set in the session, you are then
# sent on to the list.
#
# The "list" view method performs the query given the search terms in
# the session, and then pushes that list out to the template to be
# displayed. This view also handles pagination.
#
# If you like what see on the list, then you can view the "details" of
# the card.
#

def index(request):
	context = {}
	try:
		request.session['query_pred_array'] is None
	except KeyError:
		request.session['query_pred_array'] = []

	context['predicates'] = request.session.get('query_pred_array')
	context['predicates_js'] = json.dumps(request.session.get('query_pred_array'))
	context['types'] = [tt.type for tt in Type.objects.all()]
	context['subtypes'] = [st.subtype for st in Subtype.objects.all()]

	return render(request, 'cards/index.html', context)


def search(request):
	if request.session.get('query_pred_array', False):
		request.session["curpage"] = 1
		del request.session['query_pred_array']
	if request.GET.get('query', False):
		q_array = json.loads(request.GET.get('query', ''))
		logger = logging.getLogger(__name__)
		logger.error(q_array)
		request.session['query_pred_array'] = q_array

	return redirect('cards:list')


def list(request):

	# Not sure of the performance in here. Basically, I needed to
	# do a GROUP BY to get the max multiverseid and only display
	# that card. The first query here is getting the max
	# multiverseid for the given query. The second query then uses
	# that "mid_max" value to get back a list of all of the cards.
	card_listP = Card.objects.values('basecard__id').annotate(mid_max=Max('multiverseid'))
	card_list = Card.objects.filter(multiverseid__in=[g['mid_max'] for g in card_listP]).order_by('basecard__name')

	# Let's get the array of predicates from the session
	query_pred_array = []
	if request.session.get('query_pred_array', False):
		query_pred_array = request.session.get('query_pred_array')

	for pred in query_pred_array:
		if pred['field'] == 'cardname':
			if pred['op'] == 'not':
				card_list = card_list.exclude(basecard__name__icontains = pred['value'])
			else:
				card_list = card_list.filter(basecard__name__icontains = pred['value'])

		if pred['field'] == 'rules':
			if pred['op'] == 'not':
				card_list = card_list.exclude(basecard__rules_text__icontains = pred['value'])
			else:
				card_list = card_list.filter(basecard__rules_text__icontains = pred['value'])
				
		if pred['field'] == 'color':
			if pred['op'] == 'not':
				card_list = card_list.exclude(basecard__colors__in = pred['value'])
			else:
				card_list = card_list.filter(basecard__colors__in = pred['value'])

		if pred['field'] == 'cmc':
			# If it isn't an int, then skip it.
			try:
				pred['value'] = int(pred['value'])
			except ValueError:
				# we should remove this predicate. it is bogus
				query_pred_array.remove(pred)
				break
			if pred['op'] == 'lt':
				card_list = card_list.filter(basecard__cmc__lt = pred['value'])
			elif pred['op'] == 'gt':
				card_list = card_list.filter(basecard__cmc__gt = pred['value'])
			elif pred['op'] == 'ne':
				card_list = card_list.exclude(basecard__cmc__exact = pred['value'])
			else:
				# Assume equals
 				card_list = card_list.filter(basecard__cmc__exact = pred['value'])

		if pred['field'] == 'type':
			if pred['op'] == 'not':
				card_list = card_list.exclude(basecard__types__type__icontains = pred['value'])
			else:
				card_list = card_list.filter(basecard__types__type__icontains = pred['value'])

		if pred['field'] == 'subtype':
			if pred['op'] == 'not':
				card_list = card_list.exclude(basecard__subtypes__subtype__icontains = pred['value'])
			else:
				card_list = card_list.filter(basecard__subtypes__subtype__icontains = pred['value'])

		if pred['field'] == 'format':
			if pred['value'] == 'Modern_2014-09-26':
				card_list = card_list.filter(expansionset__abbr__in=['8ED','9ED','10E','M10','M11','M12','M13','M14','M15','MRD','DST','5DN','CHK','BOK','SOK','RAV','GPT','DIS','TSP','TSB','PLC','FUT','LRW','MOR','SHM','EVE','ALA','CON','ARB','ZEN','WWK','ROE','SOM','MBS','NPH','ISD','DKA','AVR','RTR','GTC','DGM','THS','BNG','JOU','KTK'])
				card_list = card_list.exclude(basecard__name__in=['Ancestral Vision','Ancient Den','Blazing Shoal','Bloodbraid Elf','Chrome Mox','Cloudpost','Dark Depths','Deathrite Shaman','Dread Return','Glimpse of Nature','Golgari Grave-Troll','Great Furnace','Green Sun\'s Zenith','Hypergenesis','Jace, the Mind Sculptor','Mental Misstep','Ponder','Preordain','Punishing Fire','Rite of Flame','Seat of the Synod','Second Sunrise','Seething Song','Sensei\'s Divining Top','Stoneforge Mystic','Skullclamp','Sword of the Meek','Tree of Tales','Umezawa\'s Jitte','Vault of Whispers'])

			elif pred['value'] == 'Modern_2014-07-18':
				card_list = card_list.filter(expansionset__abbr__in=['8ED','9ED','10E','M10','M11','M12','M13','M14','M15','MRD','DST','5DN','CHK','BOK','SOK','RAV','GPT','DIS','TSP','TSB','PLC','FUT','LRW','MOR','SHM','EVE','ALA','CON','ARB','ZEN','WWK','ROE','SOM','MBS','NPH','ISD','DKA','AVR','RTR','GTC','DGM','THS','BNG','JOU'])
				card_list = card_list.exclude(basecard__name__in=['Ancestral Vision','Ancient Den','Blazing Shoal','Bloodbraid Elf','Chrome Mox','Cloudpost','Dark Depths','Deathrite Shaman','Dread Return','Glimpse of Nature','Golgari Grave-Troll','Great Furnace','Green Sun\'s Zenith','Hypergenesis','Jace, the Mind Sculptor','Mental Misstep','Ponder','Preordain','Punishing Fire','Rite of Flame','Seat of the Synod','Second Sunrise','Seething Song','Sensei\'s Divining Top','Stoneforge Mystic','Skullclamp','Sword of the Meek','Tree of Tales','Umezawa\'s Jitte','Vault of Whispers'])

			elif pred['value'] == 'Modern_2014-05-02':
				card_list = card_list.filter(expansionset__abbr__in=['8ED','9ED','10E','M10','M11','M12','M13','M14','MRD','DST','5DN','CHK','BOK','SOK','RAV','GPT','DIS','TSP','TSB','PLC','FUT','LRW','MOR','SHM','EVE','ALA','CON','ARB','ZEN','WWK','ROE','SOM','MBS','NPH','ISD','DKA','AVR','RTR','GTC','DGM','THS','BNG','JOU'])
				card_list = card_list.exclude(basecard__name__in=['Ancestral Vision','Ancient Den','Blazing Shoal','Bloodbraid Elf','Chrome Mox','Cloudpost','Dark Depths','Deathrite Shaman','Dread Return','Glimpse of Nature','Golgari Grave-Troll','Great Furnace','Green Sun\'s Zenith','Hypergenesis','Jace, the Mind Sculptor','Mental Misstep','Ponder','Preordain','Punishing Fire','Rite of Flame','Seat of the Synod','Second Sunrise','Seething Song','Sensei\'s Divining Top','Stoneforge Mystic','Skullclamp','Sword of the Meek','Tree of Tales','Umezawa\'s Jitte','Vault of Whispers'])

			elif pred['value'] == 'Standard_2012-10-05':
				card_list = card_list.filter(expansionset__abbr__in=['M13','ISD','DKA','AVR','RTR'])
			elif pred['value'] == 'Standard_2013-02-01':
				card_list = card_list.filter(expansionset__abbr__in=['M13','ISD','DKA','AVR','RTR','GTC'])
			elif pred['value'] == 'Standard_2013-05-03':
				card_list = card_list.filter(expansionset__abbr__in=['M13','ISD','DKA','AVR','RTR','GTC','DGM'])
			elif pred['value'] == 'Standard_2013-07-19':
				card_list = card_list.filter(expansionset__abbr__in=['M13','M14','ISD','DKA','AVR','RTR','GTC','DGM'])
			elif pred['value'] == 'Standard_2013-09-27':
				card_list = card_list.filter(expansionset__abbr__in=['M14','RTR','GTC','DGM','THS'])
			elif pred['value'] == 'Standard_2014-02-07':
				card_list = card_list.filter(expansionset__abbr__in=['M14','RTR','GTC','DGM','THS','BNG'])
			elif pred['value'] == 'Standard_2014-05-02':
				card_list = card_list.filter(expansionset__abbr__in=['M14','RTR','GTC','DGM','THS','BNG','JOU'])
			elif pred['value'] == 'Standard_2014-07-18':
				card_list = card_list.filter(expansionset__abbr__in=['M14','M15','RTR','GTC','DGM','THS','BNG','JOU'])
			elif pred['value'] == 'Standard_2014-09-26':
				card_list = card_list.filter(expansionset__abbr__in=['M15','THS','BNG','JOU','KTK'])

	# Get an instance of a logger
	#logger = logging.getLogger(__name__)
	#logger.error(card_list)
	
	paginator = Paginator(card_list, 25)
	page = request.GET.get('page', request.session.get("curpage",1))
	try:
		cards = paginator.page(page)
		request.session["curpage"] = page
	except PageNotAnInteger:
		cards = paginator.page(1)
		request.session["curpage"] = 1
	except EmptyPage:
		cards = paginator.page(paginator.num_pages)
		request.session["curpage"] = paginator.num_pages
	context = {
		'cards': cards,
		'predicates': query_pred_array,
		'predicates_js': json.dumps(query_pred_array),
		}
	return render(request, 'cards/list.html', context)



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
		if card.basecard.name in card_titles:
			continue
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


def vote(request, multiverseid):
	return HttpResponse("You're voting on card %s." % multiverseid)
