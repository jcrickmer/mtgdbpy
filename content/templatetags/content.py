# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.template.defaulttags import register
import sys

#from content.models import ContentBlock

register = template.Library()
from ..models import ContentBlock


@register.filter
def concat(arg1, arg2):
    """ Concatenate arg1 and arg2 as Unicode strings
    """
    return unicode(arg1) + unicode(arg2)


@register.inclusion_tag('content.html', takes_context=True)
def content(context, key, position, title=None):
    """ Template tag render of content at key and position.
    """
    cb = ContentBlock.objects.filter(key='{}__{}'.format(key, position), status=ContentBlock.LIVE).order_by('-version').first()
    return {'title': title,
            'contentblock': cb, }
