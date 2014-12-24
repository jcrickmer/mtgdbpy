from django.utils.safestring import mark_safe
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.db.models import Max, Min, Count
from django.shortcuts import redirect
from django.http import Http404
from django.db import connection
from django.db import IntegrityError

import random
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
from mtgdbapp.models import CardRating

from django.db.models import Q

# import the logging library
import logging

from trueskill import TrueSkill, Rating, quality_1vs1, rate_1vs1

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
	except IndexError:
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


def battle(request, format="redirect"):
	logger = logging.getLogger(__name__)
	# this shows two cards at random and then let's the user decide which one is better.

	# force current standard
	if format == "redirect":
		return redirect('cards:battle', format="standard")

	format_id = 4
	test_id = 1

	format_obj = get_object_or_404(Format.objects.filter(formatname__iexact=format.lower()).order_by('-start_date')[0:1])
	format_id = format_obj.id

	# Going straight to the DB on this...
 	cursor = connection.cursor()

	card_a = None
	first_card = {
		'mu': 25.0,
		'sigma': 25.0/3.0,
		}
	second_card = {
		'mu': 25.0,
		'sigma': 25.0/3.0,
		}
	if request.GET.get('muid', False) or request.session.get('battle_cont_muid', False):
		# this is a BATTLE CHEAT so that you can battle a specific card
		cheat_list = Card.objects.filter(multiverseid__exact=request.GET.get('muid', request.session.get('battle_cont_muid', 100)))
		card_a = cheat_list[0]
		first_card['basecard_id'] = card_a.basecard.id
		crsdb = CardRating.objects.filter(physicalcard__id__exact=card_a.basecard.physicalcard.id,
										  test__id__exact=test_id,
			                              format__id__exact=format_id)
		try:
			crdb = crsdb[0]
			first_card['mu'] = crdb.mu
			first_card['sigma'] = crdb.sigma
		except IndexError:
			# no op
			logger.error("Battle: bad ju-ju finding card ratings for basecard id " + str(card_a.basecard.id))
	elif request.GET.get('bcid', False):
		# they passed us a basecard id
		cheat_list = Card.objects.filter(basecard__id__exact=int(request.GET.get('bcid', 1))).order_by('-multiverseid')
		card_a = cheat_list[0]
		first_card['basecard_id'] = card_a.basecard.id
		crsdb = CardRating.objects.filter(physicalcard__id__exact=card_a.basecard.physicalcard.id,
										  test__id__exact=test_id,
			                              format__id__exact=format_id)
		try:
			crdb = crsdb[0]
			first_card['mu'] = crdb.mu
			first_card['sigma'] = crdb.sigma
		except IndexError:
			# no op
			logger.error("Battle: bad ju-ju finding card ratings for basecard id " + str(card_a.basecard.id))
	else:
		#cursor.execute('SELECT basecard_id, RAND() r FROM mtgdbapp_formatbasecard WHERE format_id = ' + str(format_id) + ' ORDER BY r ASC LIMIT 100')
		fcsqls = 'SELECT fbc.basecard_id, cr.mu, cr.sigma, RAND() r FROM mtgdbapp_formatbasecard fbc JOIN basecards bc ON bc.id = fbc.basecard_id JOIN mtgdbapp_cardrating cr ON cr.physicalcard_id = bc.physicalcard_id WHERE fbc.format_id = ' + str(format_id) + ' ORDER BY r ASC LIMIT 1'
		logger.error("First Card SQL: " + fcsqls)
		cursor.execute(fcsqls)
		rows = cursor.fetchall()
		first_card = {
			'basecard_id': rows[0][0],
			'mu': rows[0][1],
			'sigma': rows[0][2],
			}
		card_a_list = Card.objects.filter(basecard__id__exact=rows[0][0]).order_by('-multiverseid')
		card_a = card_a_list[0]

	# now let's get a card of similar level - make it a real battle
	sqls = 'SELECT fbc.basecard_id, cr.mu, cr.sigma, RAND() r FROM mtgdbapp_formatbasecard fbc JOIN basecards bc ON bc.id = fbc.basecard_id JOIN mtgdbapp_cardrating cr ON cr.physicalcard_id = bc.physicalcard_id WHERE fbc.format_id = ' + str(format_id) + ' AND fbc.basecard_id <> ' + str(first_card['basecard_id']) + ' AND cr.mu > ' + str(first_card['mu'] - (1.5 * first_card['sigma'])) + ' AND cr.mu < ' + str(first_card['mu'] + (1.5 * first_card['sigma'])) + ' ORDER BY r ASC LIMIT 1'
	logger.error("Second Card SQL: " + sqls)
	cursor.execute(sqls)
	rows = cursor.fetchall()
	try:
		second_card = {
			'basecard_id': rows[0][0],
			'mu': rows[0][1],
			'sigma': rows[0][2],
			}
	except IndexError:
		logger.error("Battle: UGH. IndexError. This SQL returned no result: " + sqls)
		# There is always a chance that we do not get a card. That would be bad. Just fill in one of these for now.
		faked_id = random.sample([8642,2239,4644,695,6636,8621,4376,8733,933,5842,7897,5557,5553,8550,6217,8601,8530,5864,7442,8531,1764,6004,8636,1273,1704,6256,8625,108,1543,8396,6124,8664,8392,33,5766,8666,8523,8435,5999,7914,2450,1167,690,123,8568,8684,475,8373,8731,8734,4976,26,8602,5345,5191,6345,8447,8681,4466,8714,3948,8732,8637,8739,8411,8397,7552,41,7666,2059,4511,2699,878,7894,3751,3770,60,8680,8362,1381,8556,7173,8727,8520,1268], 1)
		second_card = {
			'basecard_id': faked_id,
			'mu': 25.0,
			'sigma': 8.35,
			}

	#card_b_list = Card.objects.filter(basecard__id__exact=rows[1][0]).order_by('-multiverseid')
 	card_b_list = Card.objects.filter(basecard__id__exact=second_card['basecard_id']).order_by('-multiverseid')
	card_b = card_b_list[0]
	context = {'card_a': card_a,
			   'card_b': card_b,
			   'first_card': first_card,
			   'second_card': second_card,
			   'test_id': test_id,
			   'format_id': format_id,
			   'format': format_obj,
			   }
	if request.GET.get('c', False) or request.session.get('battle_cont_muid', False):
		# let's keep card_a in rotation
		context['continue_muid'] = card_a.multiverseid
		context['continue_muid_qs'] = '&muid=' + str(card_a.multiverseid)
		# get this out of the session. we only needed it for one page turn. The next page will pass a query param if it wants it.
		if 'battle_cont_muid' in request.session:
			del request.session['battle_cont_muid']
	response = render(request, 'cards/battle.html', context)
	return response
	
def winbattle(request):
	# There is no error checking in here yet. Needs to be tested off of the happy path!
	logger = logging.getLogger(__name__)
	winning_card = None
	losing_card = None
	format = None
	format_nick = 'standard'
	test = None
 	if request.GET.get('winner', False):
		card_w_list = Card.objects.filter(multiverseid__exact=request.GET.get('winner', 0))
		winning_card = card_w_list[0]
 	if request.GET.get('loser', False):
		card_l_list = Card.objects.filter(multiverseid__exact=request.GET.get('loser', 0))
		losing_card = card_l_list[0]
 	if request.GET.get('format_id', False):
		format = Format.objects.get(pk=request.GET.get('format_id'))
		format_nick = format.formatname.lower()
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
	try:
		battle.save()
	except IntegrityError as ie:
		logger.error("Integrity Error on winning a battle... probably not a big deal: " + str(ie))

	updateRatings(battle)
	
	request.session['battle_cont_muid'] = request.GET.get('muid',False)
	return redirect('cards:battle', format=format_nick)

def updateRatings(battle):
	logger = logging.getLogger(__name__)
	ts = TrueSkill(backend='mpmath')
	crdb_w = None
	crdb_l = None
	rating_w = None
	rating_l = None

	crsdb_w = CardRating.objects.filter(physicalcard__id__exact=battle.winner_pcard.id,
										test__id__exact=battle.test.id,
		                                format__id__exact=battle.format.id)
	try:
		crdb_w = crsdb_w[0]
		rating_w = Rating(mu=crdb_w.mu, sigma=crdb_w.sigma)
	except IndexError:
		# well, that isn't good. Just be done with it. The cron job will fix it later.
		logger.error("updateRatings - could not get the CardRating for the winner. battle =" + str(battle))
		return

	crsdb_l = CardRating.objects.filter(physicalcard__id__exact=battle.loser_pcard.id,
										test__id__exact=battle.test.id,
		                                format__id__exact=battle.format.id)
	try:
		crdb_l = crsdb_l[0]
		rating_l = Rating(mu=crdb_l.mu, sigma=crdb_l.sigma)
	except IndexError:
		# well, that isn't good. Just be done with it. The cron job will fix it later.
		logger.error("updateRatings - could not get the CardRating for the loser. battle =" + str(battle))
		return

	# calculate!
	logger.error("updating battles for cards " + str(battle.winner_pcard.id) + " and " + str(battle.loser_pcard.id))
	rating_w, rating_l = rate_1vs1(rating_w, rating_l, env=ts)

	# save
	crdb_w.mu = rating_w.mu
	crdb_w.sigma = rating_w.sigma
	crdb_w.save()
	crdb_l.mu = rating_l.mu
	crdb_l.sigma = rating_l.sigma
	crdb_l.save()

	return

def vote(request, multiverseid):
	return HttpResponse("You're voting on card %s." % multiverseid)

def ratings(request):
	logger = logging.getLogger(__name__)
	format_id = 4
	test_id = 1
	# dummy test harness to just get some ratings...
	context = {}
	# REVISIT - hard coded! to subjective tet in Standard
	card_ratings = CardRating.objects.filter(format__id__exact=format_id, test__id__exact=test_id).order_by('-mu')
	context['battle_count'] = Battle.objects.filter(format__id__exact=format_id, test__id__exact=test_id).count()
	context['cards_count'] = FormatBasecard.objects.filter(format=format_id).count()
	bc = Battle.objects.filter(format__id__exact=format_id, test__id__exact=test_id).aggregate(Count('session_key', distinct=True))
	context['battlers_count'] = bc['session_key__count']
	context['battle_possibilities'] = context['cards_count'] * (context['cards_count'] - 1)
	context['battle_percentage'] = float(100) * float(context['battle_count']) / float(context['battle_possibilities'])
	context['ratings'] = []
	for rating in card_ratings:
		context['ratings'].append({'rating':rating})

 	cursor = connection.cursor()
	winnerss = 'SELECT winner_pcard_id, count(id) FROM mtgdbapp_battle WHERE format_id = ' + str(format_id) + ' AND test_id = ' + str(test_id) + ' GROUP BY winner_pcard_id'
	cursor.execute(winnerss)
	context['winners'] = cursor.fetchall()

	loserss = 'SELECT loser_pcard_id, count(id) FROM mtgdbapp_battle WHERE format_id = ' + str(format_id) + ' AND test_id = ' + str(test_id) + ' GROUP BY loser_pcard_id'
	cursor.execute(loserss)
	context['losers'] = cursor.fetchall()

	fbcards = FormatBasecard.objects.filter(format=format_id)
	for fbcard in fbcards:
		for meta in context['ratings']:
			if meta['rating'].physicalcard.id == fbcard.basecard.physicalcard.id:
				meta['basecard'] = fbcard.basecard
				for win in context['winners']:
					if win[0] == fbcard.basecard.physicalcard.id:
						meta['wins'] = win[1]
						break
				for loss in context['losers']:
					if loss[0] == fbcard.basecard.physicalcard.id:
						meta['losses'] = loss[1]
						break
				if 'losses' not in meta:
					meta['losses'] = 0
				if 'wins' not in meta:
					meta['wins'] = 0
				meta['battles'] = meta['wins'] + meta['losses']
				break

	response = render(request, 'cards/ratings.html', context)
	return response
	
