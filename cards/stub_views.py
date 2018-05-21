# -*- coding: utf-8 -*-
import sys
from cards.models import Card
import json
import random
from cards.deckbox import generate_auth_key
from django.http import HttpResponse


def card_price_ajax_stub(request, multiverseid=None, deckbox_format=False):
    sys.stderr.write("card_price_ajax_stub {} {}\n".format(multiverseid, deckbox_format))
    response_dict = {}
    auth_key = request.GET.get('key', None) or request.POST.get('key', None)
    sys.stderr.write("card_price_ajax_stub auth_key is '{}'\n".format(auth_key))
    if not auth_key or not request.session.get('deckbox_session_id') or str(auth_key).lower() != generate_auth_key(
            multiverseid,
            request.session.get('deckbox_session_id')).lower():
        multiverseid = None
        response_dict.update({'status': 'error',
                              'message': 'No authorization.', })

    card = None
    if multiverseid is not None:
        try:
            multiverseid = int(multiverseid)
            card = Card.objects.filter(multiverseid=multiverseid).order_by('card_number').first()
        except:
            response_dict.update({'status': 'error',
                                  'message': 'No such card for given multiverseid.', })
        if not deckbox_format:
            # The original format
            sys.stderr.write("  original format!\n")
            jcards = list()
            if card:
                cards = card.get_all_versions()[:8]
                for vcard in cards:
                    for printing in ('normal', 'foil'):
                        jcard = {
                            'mvid': vcard.multiverseid,
                            'name': vcard.basecard.physicalcard.get_card_name(),
                            'expansionset': {'name': vcard.expansionset.name, 'abbr': vcard.expansionset.abbr, },
                            'price': 0.75,
                            'on_sale': random.random() > 0.8,
                            'printing': printing,
                        }
                        jcards.append(jcard)
            if jcards:
                response_dict.update({'status': 'ok',
                                      'cards': jcards,
                                      })
        else:
            # The Jim/Deckbox format
            sys.stderr.write("  Deckbox format!\n")
            jcards = list()
            if int(multiverseid) in [194968, 1076]:
                # this is a test of returning the 99999999.99 answer in Unstable.
                jcard = {
                    'mvid': int(multiverseid),
                    'setname': 'Unstable',
                    'normalprice': 99999999.99,
                }
                jcards.append(jcard)
            elif card:
                cards = card.get_all_versions()[:8]
                response_dict.update({'name': card.basecard.physicalcard.get_card_name()})
                for vcard in cards:
                    fs = 0
                    if random.random() > 0.8:
                        fs = 1
                    jcard = {
                        'mvid': vcard.multiverseid,
                        'setname': vcard.expansionset.name,
                        'normalprice': 0.75,
                        'normalsale': fs
                    }
                    if random.random() > 0.6:
                        fs = 0
                        if random.random() > 0.8:
                            fs = 1
                        jcard['foil'] = 1.25
                        jcard['foilsale'] = fs
                    jcards.append(jcard)
            if jcards:
                response_dict.update({'status': 'OK',
                                      'prices': jcards,
                                      })

    response = HttpResponse(
        json.dumps(response_dict),
        content_type='application/javascript')
    return response


def card_price_deckbox_ajax_stub(request, multiverseid=None):
    # tests with Strip Mine
    if int(multiverseid) == 1077:
        return HttpResponse(
            ur'{ "status": "OK", "name": "", "prices": [{"mvid":439454, "setname":"Unstable", "normalprice":99999999.99, "normalsale":0} ]}',
            content_type='application/javascript')
    elif int(multiverseid) == 1078:
        return HttpResponse(
            ur'{ "status": "OK", "name": "Strip Mine", "prices": [{"mvid":1078, "setname":"Antiquities", "normalprice":99999999.99, "normalsale":0},{"mvid":2380, "setname":"Fourth Edition", "normalprice":8.50, "normalsale":0},{"mvid":409574, "setname":"Zendikar Expedition", "normalprice":54.00, "normalsale":1, "foilprice":9999999.99, "foilsale":0} ]}',
            content_type='application/javascript')
    elif int(multiverseid) == 1079:
        return HttpResponse(
            ur'{ "status": "OK", "name": "", "prices": [{"mvid":439454, "setname":"Unstable", "normalprice":99999999.99, "normalsale":0} ]}',
            content_type='application/javascript')
    elif int(multiverseid) == 2380:
        return HttpResponse(
            ur'{ "status": "OK", "name": "Strip Mine", "prices": [{"mvid":1078, "setname":"Antiquities", "normalprice":99999999.99, "normalsale":0},{"mvid":2380, "setname":"Fourth Edition", "normalprice":8.50, "normalsale":0},{"mvid":409574, "setname":"Zendikar Expedition", "normalprice":54.00, "normalsale":1, "foilprice":9999999.99, "foilsale":0} ]}',
            content_type='application/javascript')
    elif int(multiverseid) == 194968:
        return HttpResponse(
            ur'{ "status": "OK", "name": "", "prices": [{"mvid":439454, "setname":"Unstable", "normalprice":99999999.99, "normalsale":0} ]}',
            content_type='application/javascript')
    elif int(multiverseid) == 202433:
        return HttpResponse(
            ur'{ "status": "OK", "name": "", "prices": [{"mvid":439454, "setname":"Unstable", "normalprice":99999999.99, "normalsale":0} ]}',
            content_type='application/javascript')
    elif int(multiverseid) == 383113:
        return HttpResponse(
            ur'{ "status": "OK", "name": "", "prices": [{"mvid":439454, "setname":"Unstable", "normalprice":99999999.99, "normalsale":0} ]}',
            content_type='application/javascript')
    elif int(multiverseid) == 409574:
        return HttpResponse(
            ur'{ "status": "OK", "name": "Strip Mine", "prices": [{"mvid":1078, "setname":"Antiquities", "normalprice":99999999.99, "normalsale":0},{"mvid":2380, "setname":"Fourth Edition", "normalprice":8.50, "normalsale":0},{"mvid":409574, "setname":"Zendikar Expedition", "normalprice":54.00, "normalsale":1, "foilprice":9999999.99, "foilsale":0} ]}',
            content_type='application/javascript')
    else:
        return card_price_ajax_stub(request, multiverseid, deckbox_format=True)
