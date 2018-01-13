# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
from django.conf import settings
import re
import hashlib


def generate_auth_key(payload, session_id, secret=None):
    """ Generate an authentication key expected by Deckbox to be able to access API calls.

    This function never throws an exception. Will return None if an answer can't be figured out.

    Returns a string with the key.
    """
    try:
        if secret is None:
            secret = settings.DECKBOX_AUTH_SECRET
        m = hashlib.md5()
        #m.update('{}:{}:{}'.format(secret, session_id, payload))
        m.update('{}:{}'.format(secret, payload))
        return m.hexdigest()
    except:
        return None
