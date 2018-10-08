# -*- coding: utf-8 -*-

from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def remove_whitespace(text):
    result = text.replace("\r", " ")
    result = result.replace("\n", " ")
    breaker = 0
    while result.find("  ") > -1:
        if breaker > 100:
            break
        result = result.replace("  ", " ")
        breaker = breaker + 1
    result = result.strip()
    return result


@register.filter
def as_percentage_string(floatval, precision=2):
    if not floatval:
        floatval = 0.0
    ff = floatval * 100
    frmt = '{' + '0:.' + str(precision) + 'f}%'
    return frmt.format(ff)


@register.filter
def card_rating(physicalcard, format):
    cr = physicalcard.get_cardratings().filter(format=format).first()
    if cr is not None:
        return cr.cardninjaRating()
    else:
        return None
