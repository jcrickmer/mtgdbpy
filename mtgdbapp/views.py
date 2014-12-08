from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.db.models import Max, Min
from django.shortcuts import redirect
from django.http import Http404
from django.db import connection

import operator

from mtgdbapp.models import Card
from mtgdbapp.models import Mark
from mtgdbapp.models import Type
from mtgdbapp.models import Subtype
from mtgdbapp.models import Format
from mtgdbapp.models import FormatBasecard
from mtgdbapp.models import Ruling
from mtgdbapp.models import Rarity
from mtgdbapp.models import Battle
from mtgdbapp.models import BattleTest

from django.db.models import Q

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
	context['rarities'] = [{'id':rr.id, 'rarity':rr.rarity} for rr in Rarity.objects.all().order_by('sortorder')]
	context['formats'] = [{'format':f.format, 'formatname':f.formatname, 'start_date':f.start_date} for f in Format.objects.all().order_by('format')]

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

	# Get an instance of a logger
	logger = logging.getLogger(__name__)
	#logger.error(request)

	# Not sure of the performance in here. Basically, I needed to
	# do a GROUP BY to get the max multiverseid and only display
	# that card. The first query here is getting the max
	# multiverseid for the given query. The second query then uses
	# that "mid_max" value to get back a list of all of the cards.
	card_listP = Card.objects.values('basecard__id').annotate(mid_max=Max('multiverseid'))
	card_list = Card.objects.filter(multiverseid__in=[g['mid_max'] for g in card_listP]).order_by('basecard__filing_name')

	# Filer out the non-playing cards for now
	card_list = card_list.filter(basecard__physicalcard__layout__in = ('normal','double-faced','split','flip','leveler'))

	# Let's get the array of predicates from the session
	query_pred_array = []
	if request.session.get('query_pred_array', False):
		query_pred_array = request.session.get('query_pred_array')
		
	rlist = []
	for pred in query_pred_array:
		if pred['field'] == 'cardname':
			if pred['op'] == 'not':
				card_list = card_list.exclude(basecard__name__icontains = pred['value'])
				card_list = card_list.exclude(basecard__filing_name__icontains = pred['value'])
			else:
				card_list = card_list.filter(Q(basecard__name__icontains = pred['value']) | Q(basecard__filing_name__icontains = pred['value']))

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

		if pred['field'] == 'rarity':
			if pred['op'] == 'not':
				card_list = card_list.exclude(rarity__in = pred['value'])
			else:
				rlist.append(('rarity__exact', pred['value']))

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
			bc_vals = FormatBasecard.objects.filter(format__format__exact = pred['value']).values_list('basecard', flat=True)
			# Note that one example from Django said that I needed to do list(bc_vals). But that TOTALLY bombed, probably because list() is defined in this file. That was hard to debug.
			card_list = card_list.filter(basecard__pk__in = bc_vals)

	if len(rlist) > 0:
		card_list = card_list.filter(reduce(operator.or_, [Q(x) for x in rlist]))

	#logger.error(card_list)
	#logger.error(card_list.query)
	
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
		'ellided_prev_page': max(0, int(page) - 4),
		'ellided_next_page': min(paginator.num_pages, int(page) + 4),
		'cards': cards,
		'predicates': query_pred_array,
		'predicates_js': json.dumps(query_pred_array),
		}
	return render(request, 'cards/list.html', context)


def detail(request, multiverseid=None, slug=None):
	logger = logging.getLogger(__name__)
	cards = []
	try:
		if multiverseid is not None:
			cards = Card.objects.filter(multiverseid=multiverseid).order_by('card_number')
		elif slug is not None:
			slugws = slug.lower().replace('-', ' ')
			cards = Card.objects.filter(basecard__filing_name=slugws).order_by('card_number')
			if len(cards) > 0:
				multiverseid = cards[0].multiverseid
				return redirect('cards:detail', permanent=True, multiverseid=multiverseid, slug=slug)
			else:
				raise Http404
		else:
			raise Http404
	except Card.DoesNotExist:
		raise Http404

	# Let's see if the slub matching my filing name
	if slug is not None:
		slugws = slug.lower().replace('-', ' ')
		logger.error("slug is now \"" + slugws + "\"")
		amatch = False
		for acard in cards:
			if amatch:
				break
			amatch = amatch or (slugws == acard.basecard.filing_name)
		if not amatch:
			raise Http404
	elif not request.is_ajax():
		# we have a card with a filing_name, let's just redirect them...
		# But only redirect if it is NOT an ajax request. Let's make it easy on our ajax friends.
		newslug = cards[0].basecard.filing_name.replace(' ', '-')
		return redirect('cards:detail', permanent=True, multiverseid=multiverseid, slug=newslug)

	backCards = []
	if len(cards) > 0:
		backCards = Card.objects.filter(basecard__physicalcard__id = cards[0].basecard.physicalcard.id, expansionset__id = cards[0].expansionset.id)
		logger.error(backCards)
	cards = cards | backCards
	twinCards = Card.objects.filter(basecard__id = cards[0].basecard.id).order_by('multiverseid')
	response = HttpResponse("Lame. Something must be broken.")
	jcards = []
	card_list = []
	card_titles = []
	for card in cards:
		#logger.error('rules text: ' + card.rules_text_html())
		if card.basecard.name in card_titles:
			continue
		card_titles.append(card.basecard.name)
		
		if request.is_ajax():
			response_dict = {}
			jcard = {'name': card.basecard.name,
					 'mana_cost': card.basecard.mana_cost,
					 'mana_cost_html': card.mana_cost_html(),
					 'type': [tt.type for tt in card.basecard.types.all()],
					 'subtype': [st.subtype for st in card.basecard.subtypes.all()],
					 'text': card.rules_text_html(),
					 'flavor_text': card.flavor_text,
					 'mark': '',
					 'cmc': card.basecard.cmc,
					 'multiverseid': card.multiverseid,
					 'expansionset': {'name': card.expansionset.name, 'abbr':card.expansionset.abbr},
					 'rarity': card.rarity.rarity,
					 'card_number': card.card_number,
					 'img_url': card.img_url(),
					 'power': card.basecard.power,
					 'toughness': card.basecard.toughness,
					 'loyalty': card.basecard.loyalty,
					 'colors': [cc.color for cc in card.basecard.colors.all()]
				 }
			try:
				if card.mark is not None:
					jcard['mark'] = card.mark.mark
			except Mark.DoesNotExist:
				1
				#jcard.mark = ''
			jcards.append(jcard)
		card_list.append({'card': card, })

	if request.is_ajax():
		response_dict.update({'status': 'success', 'physicalCardTitle': " // ".join(card_titles), 'cards': jcards, })
		response = HttpResponse(json.dumps(response_dict), content_type='application/javascript')
	else:
		response = render(request, 'cards/detail.html', {'request_muid': multiverseid,
														 'cards': card_list,
														 'other_versions': twinCards,
														 'physicalCardTitle': " // ".join(card_titles),
														 #'rules_text_html': mark_safe(card.basecard.rules_text),
														 #'flavor_text_html': mark_safe(card.flavor_text),
														 #'mana_cost_html': mana_cost_html,
														 #'img_url': img_url, })
														 })
	return response


def battle(request):
	# this shows two cards at random and then let's the user decide which one is better.

	# force current standard
	format_id = 4
	cursor = connection.cursor()
	cursor.execute('SELECT basecard_id, RAND() r FROM mtgdbapp_formatbasecard WHERE format_id = ' + str(format_id) + ' ORDER BY r ASC LIMIT 2');
	rows = cursor.fetchall()

	#[{'parent_id': None, 'id': 54360982L}, {'parent_id': None, 'id': 54360880L}]
	card_a_list = Card.objects.filter(basecard__id__exact=rows[0][0]).order_by('-multiverseid')
	card_a = card_a_list[0]

	card_b_list = Card.objects.filter(basecard__id__exact=rows[1][0]).order_by('-multiverseid')
	card_b = card_b_list[0]
	context = {'card_a': card_a,
			   'card_b': card_b}
	
	response = render(request, 'cards/battle.html', context)
	return response
	
def winbattle(request):
	# There is no error checking in here yet. Needs to be tested off of the happy path!
	logger = logging.getLogger(__name__)
	winning_card = None
	losing_card = None
	format = None
	test = None
 	if request.GET.get('winner', False):
		card_w_list = Card.objects.filter(multiverseid__exact=request.GET.get('winner', 0))
		winning_card = card_w_list[0]
 	if request.GET.get('loser', False):
		card_l_list = Card.objects.filter(multiverseid__exact=request.GET.get('loser', 0))
		losing_card = card_l_list[0]
 	if request.GET.get('format_id', False):
		format = Format.objects.get(pk=request.GET.get('format_id'))
 	if request.GET.get('test_id', False):
		test = BattleTest.objects.get(pk=request.GET.get('test_id'))

	#logger.error("winner physical: " + str(winning_card.basecard.physicalcard.id))
	#logger.error("loser physical: " + str(losing_card.basecard.physicalcard.id))
	#logger.error("format: " + str(format))
	#logger.error("test: " + str(test))
	#logger.error("session: " + request.session.session_key)
	battle = Battle(test = test,
					format = format,
					winner_pcard = winning_card.basecard.physicalcard,
					loser_pcard = losing_card.basecard.physicalcard,
		            session_key = request.session.session_key)
	battle.save()
	return redirect('cards:battle')

def vote(request, multiverseid):
	return HttpResponse("You're voting on card %s." % multiverseid)
