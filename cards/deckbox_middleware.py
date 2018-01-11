# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
import uuid
import sys


class DeckboxMiddleware(object):

    """ A Middleware class that adds the Pat's Games Deckbox session information to the current users's session.
    """

    def process_request(self, request):
        deckbox_session_id = None
        deckbox_session_uuid_str = request.COOKIES.get(settings.DECKBOX_SESSION_COOKIE_KEY)
        try:
            deckbox_session_id = str(uuid.UUID(deckbox_session_uuid_str))
            request.session['deckbox_session_id'] = deckbox_session_id
        except:
            #sys.stderr.write("killed Deckbox session: {}\n".format(sys.exc_info()[0]))
            request.session['deckbox_session_id'] = None

        deckbox_order_id = None
        deckbox_order_uuid_str = request.COOKIES.get(settings.DECKBOX_ORDER_COOKIE_KEY)
        try:
            deckbox_order_id = str(uuid.UUID(deckbox_order_uuid_str))
            request.order['deckbox_order_id'] = deckbox_order_id
        except:
            #sys.stderr.write("killed Deckbox order: {}\n".format(sys.exc_info()[0]))
            request.order['deckbox_order_id'] = None

    def process_response(self, request, response):
        return response
