from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def remove_whitespace(text):
    result = text.replace(u"\r", u" ")
    result = result.replace(u"\n", u" ")
    breaker = 0
    while result.find(u"  ") > -1:
        if breaker > 100:
            break
        result = result.replace(u"  ", u" ")
        breaker = breaker + 1
    result = result.strip()
    return result
