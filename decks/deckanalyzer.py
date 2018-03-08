# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import operator
import json
import sys


class DeckManaDrawAnalyzer(object):

    def __init__(self, cursor):
        self.cursor = cursor

    BASECARD_ID = 0
    PHYSICALCARD_ID = 1
    NAME = 2
    CARDCOUNT = 3
    MANACOST = 4
    CMC = 5

    def analyze_deck_by_id(self, deck_id=73690):
        doc = dict()
        doc['id'] = deck_id
        self.cursor.execute('SELECT name FROM deck WHERE id = {}'.format(deck_id))
        for deck in self.cursor:
            doc['name'] = deck[0]

        # For the future - may also want to look at activiation costs (in rules
        # text). In doing this, skipping lands MAY not be the right thing to do.
        qq = '''SELECT bc.id, bc.physicalcard_id, bc.name, dc.cardcount, bc.mana_cost, bc.cmc FROM deckcard AS dc JOIN basecard AS bc ON dc.physicalcard_id = bc.physicalcard_id JOIN cardtype AS ct ON ct.basecard_id = bc.id JOIN type AS t ON t.id = ct.type_id WHERE t.type != 'Land' AND deck_id = {} GROUP BY bc.id'''.format(
            deck_id)

        #colors = ['{w/u}','{r/g}','{w/b}','{g/w}','{b/g}','{u/b}','{g/u}','{u/r}','{r/w}','{b/r}','{2/w}','{2/u}','{2/b}','{2/r}','{2/g}']
        #phyrexian_colors = ['{b/p}','{u/p}','{w/p}','{r/p}','{g/p}']

        self.cursor.execute(qq)
        return self.analyze_deck_by_iterable(self.cursor, doc)

    def analyze_deck_by_iterable(self, table, doc):
        doc['x_f'] = 0
        for color in ('cmc', 'w', 'u', 'b', 'r', 'g', 'c'):
            doc['{}_f'.format(color)] = 0.0
            for cmc in range(0, 18):
                doc['{}{}_f'.format(color, int(cmc))] = 0.0
        total_cmc = 0
        card_count = 0
        for card in table:
            #sys.stderr.write("card: {}\n".format(card))
            doc['cmc{}_f'.format(int(card[DeckManaDrawAnalyzer.CMC]))] = doc[
                'cmc{}_f'.format(card[DeckManaDrawAnalyzer.CMC])] + float(card[DeckManaDrawAnalyzer.CARDCOUNT])
            total_cmc = total_cmc + (float(card[DeckManaDrawAnalyzer.CARDCOUNT]) * float(card[DeckManaDrawAnalyzer.CMC]))
            card_count = int(card_count) + int(card[DeckManaDrawAnalyzer.CARDCOUNT])
            if card[DeckManaDrawAnalyzer.MANACOST]:
                # cards with x in cost
                doc['x_f'] = doc['x_f'] + \
                    (float(card[DeckManaDrawAnalyzer.CARDCOUNT]) * float(card[DeckManaDrawAnalyzer.MANACOST].count('{x}')))
                for color in ('w', 'u', 'b', 'r', 'g', 'c'):
                    pip_key = '{}_f'.format(color)
                    cmc_key = '{}{}_f'.format(color, int(card[DeckManaDrawAnalyzer.CMC]))
                    add_val = (float(card[DeckManaDrawAnalyzer.CARDCOUNT]) * card[DeckManaDrawAnalyzer.MANACOST].count('{' + color + '}'))
                    add_val = add_val + (float(card[DeckManaDrawAnalyzer.CARDCOUNT]) * 0.5 *
                                         card[DeckManaDrawAnalyzer.MANACOST].count('{' + color + '/'))
                    add_val = add_val + (float(card[DeckManaDrawAnalyzer.CARDCOUNT]) * 0.5 *
                                         card[DeckManaDrawAnalyzer.MANACOST].count('/' + color + '}'))
                    doc[pip_key] = doc[pip_key] + add_val
                    doc[cmc_key] = doc[cmc_key] + add_val
        if card_count:
            doc['cmc'] = float(total_cmc) / float(card_count)
        else:
            doc['cmc'] = -1.0
        return doc

    def distance_strat(self, val):
        return float(val) * val * 0.45

    def pip_distance_strat(self, val):
        return float(val) * val * 0.85

    def score(self, query, corpus):
        # loop through the corpus, finding things that are close and scoring them.
        OPTIMIZATION_LIMIT = 40 * 4 * 1.75
        top_score = OPTIMIZATION_LIMIT
        scores = dict()
        for key in corpus:
            scores[key] = 0.0
            doc = corpus[key]
            for qkey in query:
                qval = query[qkey]
                if qkey in ('w_f', 'u_f', 'b_f', 'r_f', 'g_f', 'c_f'):
                    # BOOST
                    scores[key] = scores[key] + self.pip_distance_strat(abs(doc[qkey] - qval))
                else:
                    scores[key] = scores[key] + self.distance_strat(abs(doc[qkey] - qval))
                if scores[key] > (top_score * 1.05):
                    # we know that this is too far out... stop looking.
                    scores.pop(key, None)
                    break
            if key in scores:
                top_score = max(top_score, scores[key])
        scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=False)

        return scores
