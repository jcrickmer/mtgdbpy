# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#import mysql.connector
#from  mysql.connector import connection
import operator
import sys


class DeckCardRecommender(object):

    def __init__(self, cursor):
        self.cursor = cursor
        self.DECAY = 0.85
        self.LOOKBACK_REL_DENOM_DAYS = 1.1 * 365

    def get_decks_for_physicalcard(self, pcard_id, formatname, result=dict()):
        ''' For the card pcard_id, find all decks in formatname.
        '''
        # REVISIT - we need a way to SAMPLE this list somewhat randomly, with more
        # attention paid to recent rather than old. Just sorting by format end
        # date and limitting to 50 is not good enough.
        self.cursor.execute(
            "SELECT dc.deck_id, DATEDIFF(CURDATE(), f.start_date) AS days_old FROM deckcard AS dc JOIN deck AS d ON d.id = dc.deck_id JOIN format AS f ON f.id = d.format_id WHERE f.formatname = '{}' AND dc.physicalcard_id = {} AND f.end_date > SUBDATE(CURDATE(), INTERVAL 2 YEAR)".format(
                formatname,
                pcard_id))
        for ll in self.cursor:
            score_val = 1 - (ll[1] / 772.0)
            if ll[0] not in result:
                result[ll[0]] = score_val
            else:
                result[ll[0]] = score_val + result[ll[0]]
        return result

    def _sort_recommendations(self, pcard_scores):
        ''' Takes in a dict of physicalcard_id/count pairs and sorts them by count, returning a list of tuples (physicalcard_id, score)
        '''
        return sorted(pcard_scores.items(), key=operator.itemgetter(1), reverse=True)

    def get_recommendations_decklists(self, physicalcard_ids, formatname='Modern', include_seeds=False, k=20):
        deck_ids = dict()
        for ccc in physicalcard_ids:
            deck_ids = self.get_decks_for_physicalcard(ccc, formatname, result=deck_ids)

        deck_ids = self._sort_recommendations(deck_ids)
        
        pcard_scores = dict()
        it_count = 0
        for deck_id in deck_ids:
            it_count = it_count + 1
            #self.cursor.execute('SELECT dc.physicalcard_id, dc.cardcount, DATEDIFF(CURDATE(), CASE WHEN t.start_date IS NOT NULL THEN t.start_date ELSE SUBDATE(CURDATE(), INTERVAL 2 YEAR) END) AS days_old FROM deckcard AS dc JOIN deck AS d ON dc.deck_id = d.id LEFT JOIN tournamentdeck AS td ON td.deck_id = d.id LEFT JOIN tournament AS t ON td.tournament_id = t.id WHERE dc.deck_id = {}'.format(deck_id[0]))
            self.cursor.execute(
                'SELECT dc.physicalcard_id, dc.cardcount, DATEDIFF(CURDATE(), t.start_date) AS days_old FROM deckcard AS dc JOIN deck AS d ON dc.deck_id = d.id LEFT JOIN tournamentdeck AS td ON td.deck_id = d.id LEFT JOIN tournament AS t ON td.tournament_id = t.id WHERE dc.deck_id = {}'.format(
                    deck_id[0]))
            touched_ids = list()
            for ll in self.cursor:
                c_pcard_id = ll[0]
                c_cardcount = ll[1] or 1
                c_age = ll[2]
                if c_age is None:
                    # Let's give this guy the benefit of the doubt... it is half as old as we care about.
                    c_age = self.LOOKBACK_REL_DENOM_DAYS / 2
                ov = float(0)
                if c_pcard_id in pcard_scores:
                    ov = pcard_scores[c_pcard_id]
                # Base score is +1.
                #
                # Then, subtract the age of the last time that this card was used as a precentage of the total lookback time that we care
                # about, represented by self.LOOKBACK_REL_DENOM_DAYS. But, let's not let that get bigger than 1.
                #
                # This, let's use the cardcount as a means of expressing how valuable this card is to the deck. REVISIT - assuming deck
                # size of 75 for now.
                pcard_scores[c_pcard_id] = 1 - \
                    (min(c_age, self.LOOKBACK_REL_DENOM_DAYS - 1) / self.LOOKBACK_REL_DENOM_DAYS) + (.25 * (c_cardcount / 75)) + ov
                touched_ids.append(c_pcard_id)
                # print "{} {} {}".format(c_pcard_id, c_cardcount, c_age)
            # penalize the missing
            for pckey in pcard_scores:
                if pckey not in touched_ids:
                    pcard_scores[pckey] = pcard_scores[pckey] - self.DECAY
            if it_count > 50:
                break
        result = self._sort_recommendations(pcard_scores)
        if not include_seeds:
            newres = list()
            for aa in result:
                if aa[0] not in physicalcard_ids:
                    newres.append(aa)
            result = newres

        # limit the results to just the max asked for, k
        limitted = list()
        kcnt = 0
        for res in result:
            limitted.append(res)
            kcnt = kcnt + 1
            if kcnt >= k:
                break
        result = limitted

        return result

    def get_recommendations(self, physicalcard_ids, formatname='Modern', include_seeds=False, k=20):
        #sys.stderr.write("yo get_recommendations {} {}\n".format(physicalcard_ids, formatname))
        return self.get_recommendations_decklists(physicalcard_ids, formatname, include_seeds, k)
