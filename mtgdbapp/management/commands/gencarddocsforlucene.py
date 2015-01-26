from django.core.management.base import BaseCommand, CommandError
from mtgdbapp.models import Card
from mtgdbapp.models import PhysicalCard

import re

from optparse import make_option

from datetime import datetime, timedelta

import codecs

import sys
out = sys.stdout


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Generate HTML links to do battles on the cards that are entered on stdin.'

    option_list = BaseCommand.option_list + (
        make_option('--outdir',
                    dest='outdir',
                    type='string',
                    default='./',
                    help='The directory to stick all of these documents.'),
    )

    def handle(self, *args, **options):

        pcard_list = PhysicalCard.objects.all()
        #pcard_list = PhysicalCard.objects.filter(id__lt=200)

        output_type = 'no_name'

        for pcard in pcard_list:
            if pcard.layout in [pcard.TOKEN, pcard.PLANE, pcard.SCHEME, pcard.PHENOMENON, pcard.VANGUARD]:
                continue

            fileout = codecs.open(options['outdir'] + '/' + str(pcard.id), 'w', 'utf-8')
            if output_type != 'just_rules':
                fileout.write('layout' + pcard.layout + "\n")

            for basecard in pcard.basecard_set.all():
                rules = basecard.rules_text
                rules = rules.replace(basecard.name,'cardselfreference')
                rules = rules.lower()
                rules = rules.replace('{t}',' tap ')
                rules = rules.replace('{q}',' untap ')
                rules = rules.replace('{w}',' manawhite ')
                rules = rules.replace('{u}',' manablue ')
                rules = rules.replace('{b}',' manablack ')
                rules = rules.replace('{r}',' manared ')
                rules = rules.replace('{g}',' managreen ')
                rules = rules.replace('{x}',' manax ')
                for numm in range(0,20):
                    rules = rules.replace('{' + str(numm) + '}','mana' + str(numm))
                rules = rules.replace("{wp}", ' mamawhite manaphyrexian ')
                rules = rules.replace("{up}", ' mamablue manaphyrexian ')
                rules = rules.replace("{bp}", ' mamawhite manaphyrexian ')
                rules = rules.replace("{rp}", ' mamawhite manaphyrexian ')
                rules = rules.replace("{gp}", ' mamawhite manaphyrexian ')
                rules = rules.replace("{2w}", ' manaalt2 manawhite ')
                rules = rules.replace("{2u}", ' manaalt2 manablue ')
                rules = rules.replace("{2b}", ' manaalt2 manablack ')
                rules = rules.replace("{2r}", ' manaalt2 manared ')
                rules = rules.replace("{2g}", ' manaalt2 managreen ')
                rules = rules.replace("{wu}", ' manawhite manablue ')
                rules = rules.replace("{wb}", ' manawhite manablack ')
                rules = rules.replace("{ub}", ' manablue manablack ')
                rules = rules.replace("{ur}", ' manablue manared ')
                rules = rules.replace("{br}", ' manablack manared ')
                rules = rules.replace("{bg}", ' manablack managreen ')
                rules = rules.replace("{rg}", ' manared managreen ')
                rules = rules.replace("{rw}", ' manared manawhite ')
                rules = rules.replace("{gw}", ' managreen manawhite ')
                rules = rules.replace("{gu}", ' managreen manablue ')

                # need to add something that does a regexp match on hybrid mana in mana cost and rules text and adds a term for 'manahybrid'

                if output_type == 'just_rules':
                    fileout.write(basecard.rules_text + "\n")
                else:
                    if output_type != 'no_name':
                        fileout.write(basecard.name + "\n")
                        fileout.write(basecard.filing_name + "\n")
                    fileout.write(rules + "\n")
                    fileout.write(basecard.mana_cost + "\n")
                    strippedcost = str(basecard.mana_cost).replace('{','')
                    strippedcost = strippedcost.replace('}','')
                    strippedcost = strippedcost.replace('/p','')
                    strippedcost = strippedcost.replace('2/','')
                    strippedcost = strippedcost.replace('/','')
                    fileout.write(strippedcost.lower() + "\n")
                    uses_pmana = False
                    try:
                        basecard.rules_text.lower().index('/p}')
                        uses_pmana = True
                    except ValueError:
                        pass
                    try:
                        basecard.mana_cost.lower().index('/p}')
                        uses_pmana = True
                    except ValueError:
                        pass
                    if uses_pmana:
                        fileout.write('phyrexianmana\n')
                    fileout.write('cmc' + str(basecard.cmc) + "\n")
                    if basecard.power is not None:
                        fileout.write('power' + str(basecard.power) + "\n")                
                    if basecard.toughness is not None:
                        fileout.write('toughness' + str(basecard.toughness) + "\n")                
                    if basecard.loyalty is not None:
                        fileout.write('loyalty' + str(basecard.loyalty) + "\n")                
                    colors = basecard.colors.all()
                    if len(colors) > 1:
                        fileout.write('multicolored\n')
                    else:
                        fileout.write('notmulticolored\n')
                    allcolors = ['white','blue','black','red','green','colorless']
                    for color in colors:
                        fileout.write('cardcolor' + color.color.lower() + "\n")
                        allcolors.remove(color.color.lower())
                    for notcolor in allcolors:
                        fileout.write('notcardcolor' + notcolor + "\n")
                        
                    fileout.write(' '.join('type' + ctype.type for ctype in basecard.types.all()) + "\n")
                    fileout.write(' '.join('subtype' + cstype.subtype for cstype in basecard.subtypes.all()) + "\n")

            fileout.write("\n")
            fileout.close()
