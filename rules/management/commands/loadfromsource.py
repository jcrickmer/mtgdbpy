# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from xml.dom.minidom import parse, parseString
from django.utils import timezone
#from django.utils.dateparse import parse_datetime
import datetime
import codecs
import logging
import sys
import json
import re
import sys
from operator import itemgetter

from rules.models import Rule, Example, RulesMeta

from cards.view_utils import convertSymbolsToHTML
from cards.models import PhysicalCard, BaseCard


class Command(BaseCommand):

    def handle(self, *args, **options):
        UTF8Writer = codecs.getwriter('utf8')
        outer = UTF8Writer(sys.stdout)
        logger = logging.getLogger(__name__)

        # Downloaded docx version of rules - http://archive.wizards.com/Magic/tcg/article.aspx?x=magic/rules
        # opened it in Word, and then saved it as htm with the encoding set to UTF-8 in the Web Options settings.
        # Make it XML so that xml.dom can play with it
        # xmllint --html --xmlout MagicCompRules_20140601.htm  > fixed.html
        infile = codecs.open('/home/jason/projects/mtgdb/rules.html', 'r', 'utf-8')
        bigstring = infile.read()
        dom = parseString(bigstring.encode('UTF-8'))
        divs = dom.getElementsByTagName('div')
        div = divs.item(0)

        # Axe all of the current data
        Example.objects.all().delete()
        Rule.objects.all().delete()
        RulesMeta.objects.all().delete()

        rulesmeta = None

        card_vals = self.init_cards()

        markers_passed = list()
        header_re = re.compile('^(\d{1,2})\\.\s+(\S.+)$', re.UNICODE)
        rule_re = re.compile('^(\d\d\d)\\.?((\d{1,3})([a-z])?)?\\.?\s+(\S.+)$', re.UNICODE)
        example_re = re.compile('^\s*\\<[Bb]\\>[Ee]xample[^\\<]*\\</[Bb]\\>:?\\.?\s*(\S.+)$', re.UNICODE)
        has_letter_re = re.compile('[a-z]', re.I)
        effectivedate_re = re.compile('These rules are effective as of ([^\\.]+).', re.U)
        current_header = None
        parent_rule = None
        current_rule = None
        current_header_r = None
        parent_rule_r = None
        current_rule_r = None
        example_position = 0
        for element in div.childNodes:
            if element.nodeType == element.ELEMENT_NODE and element.tagName == 'p':
                stringback = self.cleanTextFromNode(element.childNodes)
                if stringback == 'Contents' or stringback == 'Glossary' or stringback == 'Credits':
                    markers_passed.append(stringback)
                    if 'Contents' in markers_passed and 'Glossary' in markers_passed and 'Credits' in markers_passed and stringback == u'Glossary':
                        break
                    continue
                if 'Contents' in markers_passed and 'Glossary' in markers_passed and 'Credits' in markers_passed:
                    if len(stringback) > 0:
                        header_match = header_re.match(stringback)
                        if header_match:
                            dfg = u'HEADER!!! __{}__ --{}--\n'.format(header_match.group(1), header_match.group(2)).encode('utf8')
                            current_header = header_match.group(1)
                            current_rule = None
                            #dfg = match.group(0).encode('utf8')
                            sys.stdout.write(dfg)
                            # now the real work
                            hRule = Rule(section=header_match.group(1).encode('utf8'), rule_text=header_match.group(2).encode('utf8'))
                            hRule.save()
                            current_header_r = hRule
                        else:
                            rule_match = rule_re.match(stringback)
                            if rule_match:
                                current_rule = rule_match.group(1)
                                dfg = u'RULE {}, 1"{}" 3"{}" 4"{}": {}\n'.format(
                                    current_header,
                                    rule_match.group(1),
                                    rule_match.group(3),
                                    rule_match.group(4),
                                    rule_match.group(5)).encode('utf8')
                                sys.stdout.write(dfg)
                                # now the real work
                                part1 = rule_match.group(1)
                                part2 = rule_match.group(3)
                                part3 = rule_match.group(4)
                                combined = part1
                                sorty = part1
                                dParent = None
                                if part2 is None and part3 is None:
                                    # parent is a header
                                    dParent = part1[0]  # hard coded to first character for now
                                else:
                                    combined = u'{}.{}'.format(part1, part2)
                                    sorty = u'{0:0>3}.{1:0>3}'.format(part1, part2)
                                    dParent = part1
                                    if part3 is not None:
                                        dParent = u'{}.{}'.format(part1, part2)
                                        combined = u'{}{}'.format(combined, part3)
                                        sorty = u'{0}{1: >2}'.format(sorty, part3)
                                sys.stdout.write('Looking for parent ' + dParent + "\n")
                                parent_q = Rule.objects.filter(section__iexact=dParent)
                                parent_r = parent_q.first()
                                if parent_r is None:
                                    sys.stdout.write("SQL: " + str(parent_q.query) + "\n")
                                    quit()
                                rule_text_html = self.markup_text(rule_match.group(5), card_vals)
                                rRule = Rule(
                                    parent=parent_r,
                                    section=combined.encode('utf8'),
                                    sortsection=sorty.encode('utf8'),
                                    rule_text=rule_match.group(5).encode('utf8'),
                                    rule_text_html=rule_text_html)
                                rRule.save()
                                current_rule_r = rRule
                                example_position = 0
                            else:
                                example_match = example_re.match(stringback)
                                if example_match:
                                    dfg = u'  EXAMPLE {}, {}: {}\n'.format(
                                        current_header,
                                        current_rule,
                                        example_match.group(1)).encode('utf8')

                                    sys.stdout.write(dfg)
                                    # Now do the real work
                                    example_db = Example(
                                        position=example_position,
                                        rule=current_rule_r,
                                        example_text=example_match.group(1).encode('utf8'),
                                        example_text_html=self.markup_text(example_match.group(1), card_vals))
                                    example_db.save()
                                    example_position = example_position + 1
                                else:
                                    sys.stdout.write(u'ACK!! {}\n'.format(stringback).encode('utf8'))
                else:
                    ed_m = effectivedate_re.match(stringback)
                    if ed_m and rulesmeta is None:
                        # more code goes in here...
                        rulesmeta = RulesMeta()
                        rulesmeta.source_url = 'http://media.wizards.com/images/magic/tcg/resources/rules/MagicCompRules_20150327.pdf'
                        rulesmeta.effective_date = datetime.date(2015, 3, 27)
                        rulesmeta.import_date = timezone.now()
                        rulesmeta.save()

    def cleanTextFromNode(self, nodeList):
        empty_re = re.compile('\\<[Pp]\\>\s+\\</[Pp]\\>', re.U)
        space_re = re.compile('\\<[BUIAbuia]\\>\s+\\</[BUIAbuia]\\>', re.U)
        result = u''
        for pnode in nodeList:
            if pnode.nodeType == pnode.TEXT_NODE:
                result = u'{}{}'.format(result, pnode.data)
                result = result.strip(u'\r')
                result = result.replace(u'\n', u' ')
                result = result.replace(u'\t', u' ')
                result = result.replace(u"\xa0", u' ')
            if pnode.nodeType == pnode.ELEMENT_NODE:
                recurse = self.cleanTextFromNode(pnode.childNodes)
                if len(recurse) > 1:
                    #recurse = recurse.strip()
                    pass
                if len(recurse) > 0:
                    if pnode.tagName == 'span' or pnode.tagName == 'a':
                        # MS Word only used span for putting OLE anchor refs. we don't need that.
                        result = result + recurse
                    else:
                        #result = u'{}<{}>{}</{}>'.format(result.encode('utf8'), pnode.tagName.encode('utf8'), recurse.encode('utf8'), pnode.tagName.encode('utf8'))
                        result = u'{}<{}>{}</{}>'.format(result, pnode.tagName.encode('utf8'), recurse, pnode.tagName.encode('utf8'))
                        # sys.stdout.write(u"@@@@@@")
                        # sys.stdout.write(result.encode('utf8'))
                        # sys.stdout.write(u"@@@@@@@\n")
                        if empty_re.match(result):
                            result = u''
                        elif space_re.search(result):
                            #sys.stdout.write("SPACE MATCH YO\n")
                            result = space_re.sub(u' ', result)
        return result

    def markup_text(self, text, card_vals):
        # First, let's look for rule references
        ruleref_re = re.compile(r'((\d\d\d)\.(\d{1,3}[a-z]?))', re.U)
        result = ruleref_re.sub(r'<a href="\2#\1">\1</a>', text)
        ruleref2_re = re.compile(r'([Rr]ule) (\d\d\d)', re.U)
        result = ruleref2_re.sub(r'\1 <a href="\2">\2</a>', result)

        # Get all of the cards, and replace them!
        for simplecard in card_vals:
            nre = re.compile(u'([^>a-zA-Z]){}([^<a-zA-Z])'.format(simplecard['name']), re.U)
            result = nre.sub(
                u'\\1<a href="/cards/{}-{}/">{}</a>\\2'.format(simplecard['multiverseid'], simplecard['url_slug'], simplecard['cleanname']), result)
            nre2 = re.compile(u'^{}'.format(simplecard['name']), re.U)
            result = nre2.sub(
                u'<a href="/cards/{}-{}/">{}</a>'.format(simplecard['multiverseid'], simplecard['url_slug'], simplecard['cleanname']), result)
        result = convertSymbolsToHTML(result)
        return result

    def init_cards(self):
        result = list()
        #bcards = BaseCard.objects.filter(physicalcard_id__gt=7400, physicalcard_id__lt=7500).order_by('-filing_name')
        bcards = BaseCard.objects.all().order_by('-filing_name')
        for basecard in bcards:
            card = basecard.physicalcard.get_latest_card()
            simple = {'name': basecard.name,
                      'cleanname': basecard.name,
                      'url_slug': card.url_slug(),
                      'name_len': len(basecard.name),
                      'multiverseid': card.multiverseid}
            result.append(simple)
            try:
                if basecard.name.index("'"):
                    simple = {'name': basecard.name.replace(u"'", u"’"),
                              'cleanname': basecard.name,
                              'url_slug': card.url_slug(),
                              'name_len': len(basecard.name),
                              'multiverseid': card.multiverseid}
                    result.append(simple)
            except ValueError:
                pass
            for sillydash in [u'–', u'—', u'‒', u'-']:
                try:
                    if basecard.name.index(sillydash):
                        simple = {'name': basecard.name.replace(sillydash, u'-'),
                                  'cleanname': basecard.name,
                                  'url_slug': card.url_slug(),
                                  'name_len': len(basecard.name),
                                  'multiverseid': card.multiverseid}
                        result.append(simple)
                except ValueError:
                    pass
                try:
                    if simple['name'].index('-'):
                        simple = {'name': basecard.name.replace('-', sillydash),
                                  'cleanname': basecard.name,
                                  'url_slug': card.url_slug(),
                                  'name_len': len(basecard.name),
                                  'multiverseid': card.multiverseid}
                        result.append(simple)
                except ValueError:
                    pass

        result = sorted(result, key=itemgetter('name_len'), reverse=True)
        return result
