from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.utils.safestring import mark_safe
import re
from rules.models import RulesMeta, Rule, Example


def index(request):
    headers = Rule.objects.filter(parent=None)
    meta = RulesMeta.objects.all().first()
    context = {'rules': headers,
               'meta': meta,
               'doc_title': 'foo'}
    return render(request, 'rules/index.html', context)


def showsection(request, section='100'):
    context = dict()
    try:
        rule = Rule.objects.filter(section=section).first()
        meta = RulesMeta.objects.all().first()
        allsections = Rule.objects.filter(parent__parent__isnull=True, parent__isnull=False).order_by('section')
        previous_rule = None
        next_rule = None
        its_next = False
        for grule in allsections:
            if its_next:
                next_rule = grule
                break
            if grule.id == rule.id:
                its_next = True
            else:
                previous_rule = grule

        context = {'rule': rule,
                   'meta': meta,
                   'previous_rule': previous_rule,
                   'next_rule': next_rule,
                   }
        return render(request, 'rules/rule.html', context)
    except IOError as ioe:
        raise Http404


def shDDDowdoc(request, path=None):
    context = dict()
    try:
        context['path'] = path
        context['doc_body'] = ''
        if path is not None:
            path.replace('..', '_')
            path.replace('/', '_')
            path.replace('\\', '_')
            doc = open('/home/jason/projects/mtgstats/clean_rules/{}.html'.format(path), 'r')
            raw_doc = str(doc.read())
            pattern = re.compile('<h1><p>([^<]+)</p></h1>')
            matches = pattern.match(raw_doc)
            context['doc_title'] = matches.group(1)
            cleaned_doc = pattern.sub('', raw_doc, 1)
            context['doc_body'] = mark_safe(cleaned_doc)
        return render(request, 'rules/index.html', context)
    except IOError as ioe:
        raise Http404
