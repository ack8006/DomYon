from __future__ import division

import sys
sys.dont_write_bytecode = True
import inspect
from collections import defaultdict
from random import shuffle

import card_classes as cc
# from game_play import Player

'''To Implement Notes

VALUATION
- Need Chapel Valuation Metric

ACTION
- Highest inc in expected value
- Need Differences between 1 action remaining and two actions remaining
- Need Chapel Logic, compare average hand value after using chapel with average hand value after playing a card and whatever I would do on the next turn
- Consider mandatory chapel first buy on 2/3

VICTORY
- Can calculate Probabilities of getting an 8 vs opponent probaiblity getting an 8. Then from there can decide when to start buying.
- Need Victory Buy Logic

'''

class Domyon(object):
    def __init__(self):
    #def __init__(self, card_dict):
        self.card_dict = self.get_card_dict()
        self.buy_filter = ['Province', 'Silver','Gold','Festival','Laboratory','Market','Smithy','Village']
        self.round = 0

    def action_choice(self, player_info):
    #First, look for any card that provides additional actions, order not as important currently 
        for c in player_info.actions_available:
            if isinstance(c, str):
                c = self.card_dict[c]
            if c.gain_actions >= 1:
                return c.name
        #Otherwise, play card that give best expected value
        #Should consider number of remaining actions, if 2+ perhaps plays smithy to have chance of more actions
        #if not, simple best next card

        action_names = []
        for x in player_info.actions_available:
            if not isinstance(x, str):
                x = x.name
            action_names.append(x)

        if 'Chapel' in action_names and len(self.cop_est_count(player_info)) >=2:
            return 'Chapel'
        if 'Smithy' in action_names:
            return 'Smithy'
        # if 'Chapel' in player_info.actions_available and len(self.cop_est_count(player_info)) >=2:
        #     return 'Chapel'
        # if 'Smithy' in player_info.actions_available:
        #     return 'Smithy'
        return 'None'

    def execute_action_strategy(self, player_info, action):
        if action.name == 'Chapel':
            # print self.cop_est_count(player_info)
            return self.cop_est_count(player_info)

    def cop_est_count(self, player_info):
        return [x for x in player_info.hand if x in ['Copper', 'Estate']][:4]

    def clean_card_name(self, x):
        return x.replace(' ','').lower().title()

    def str_cc_filter(self, x, treas):
        if isinstance(x, str):
            x = self.card_dict[self.clean_card_name(x)]
        if x.cost <= treas:
            return True
        return False

    def buy_choice(self, player_info):
        # print player_info.treasure
        available_cards = list(filter(lambda x: self.str_cc_filter(x, player_info.treasure), 
                                      player_info.bank.keys()))
        # available_cards = list(filter(lambda x: self.card_dict[self.clean_card_name(x)].cost <= player_info.treasure, 
        #                               player_info.bank.keys()))
        available_cards = [x for x in available_cards if x in self.buy_filter]

        self.round += 1
        if self.round <= 2 and player_info.treasure <= 3:
            return 'Chapel'
        elif self.round <= 2 and player_info.treasure == 5:
            return 'Laboratory'
        elif self.round <= 2 and player_info.treasure == 4:
            return 'Silver'

        if 'Province' in available_cards:
            return 'Province'
        elif player_info.treasure >= 5 and player_info.bank['Province'] <= 4 and player_info.bank['Duchy'] > 0:
            return 'Duchy'

        average_scores = defaultdict(int)
        GT5 = defaultdict(int)
        GT8 = defaultdict(int)
        scores = self.avg_hand_value(player_info)
        average_scores['None'] = self.calc_avg_score(scores)
        GT5['None'] = self.calc_gt_x(scores, 5)
        GT8['None'] = self.calc_gt_x(scores, 8)

        for c in available_cards:
            scores = self.avg_hand_value(player_info, [c])
            average_scores[c] = self.calc_avg_score(scores)
            GT5[c] = self.calc_gt_x(scores, 5)
            GT8[c] = self.calc_gt_x(scores, 8)

        # self.pretty_print_dict(average_scores, 'Average Scores') 
        # self.pretty_print_dict(GT5, 'Greater Than Five:') 
        # self.pretty_print_dict(GT8, 'Greater Than Eight') 
        buy_choice = max(average_scores.iterkeys(), key=(lambda key: average_scores[key]))
        return buy_choice

    def calc_avg_score(self, scores):
        return sum(k*v for k,v in scores.iteritems()) / sum(v for v in scores.values())

    def calc_gt_x(self, scores, x):
        return sum(v for k,v in scores.iteritems() if k>=x) / sum(v for v in scores.values())

    def pretty_print_dict(self, d, name, limit = 5):
        print name
        for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True)[:limit]:
            print k, ': ', v
        print ''

    #could montecarlo once action choice is set?
    def deck_value(self, player_info, cards=None):
        #treasure first
        combined = player_info.deck
        if cards:
            combined += cards
        total_val = 0
        total_val += sum([x.treasure for x in combined if x.grouping == 'Treasure'])
        return total_val / len(combined)

    def avg_hand_value(self, player_info, cards=None, its = 100):
        scores = defaultdict(int)
        for x in xrange(its):
            p = TempPlayer()
            p.discard = [x for x in player_info.deck] + [x for x in player_info.discard] + [x for x in player_info.hand]
            if cards:
                p.discard += cards
            p.draw_cards(5)
            p.treasure = 0
            p.actions_remaining = 1

            scores[self.hand_value(p, cards)] += 1
            del p
        return scores

    '''Given full info, will calculated hand value based on player info parameters'''
    def hand_value(self, p, cards=None):
        while p.actions_remaining > 0:
            p.actions_available = [x for x in p.hand if self.card_dict[x].grouping == 'Action']
            # if not p.actions_available:
            #     break
            action = self.action_choice(p)
            if action == 'None':
                break
            elif isinstance(action, str):
                action = self.card_dict[action]
            p = self.update_player(p, action)

        total_val = 0
        total_val += sum([self.card_dict[x].treasure for x in p.hand if self.card_dict[x].grouping == 'Treasure'])
        total_val += p.treasure

        return total_val

    def update_player(self, p, card):
        if card != 'None':
            p.hand.remove(card.name)
            p.actions_remaining += -1 + card.gain_actions
        p.draw_cards(card.draw_cards)
        #p.buys += card.gain_buys
        p.treasure += card.gain_treasure
        return p

    def get_card_dict(self):
        card_dict = {}
        for name, obj in inspect.getmembers(cc):
            if inspect.isclass(obj):
                card_dict[name] = obj()
        return card_dict

class TempPlayer(object):
    def __init__(self):
        self.deck = []
        self.hand = []
        self.discard = []
        self.played_actions = []

    def shuffle_discards(self):
        self.deck.extend(self.discard)
        shuffle(self.deck)
        self.discard = []

    def draw_cards(self, num):
        for x in range(0,num):
            if len(self.deck) == 0:
                if len(self.discard) ==0:
                    break
                self.shuffle_discards()
            card_type = self.deck.pop(0)
            self.hand.append(card_type)




def main():
    # card_dict = get_card_dict()

    # player_info = Player()
    # player_info.deck = ['Copper'] * 7 + ['Estate'] * 3 #+ ['Smithy'] * 1+ ['Silver'] * 1
    # player_info.deck = ['Copper'] * 7 + ['Estate'] * 3 + ['Festival']# * 1+ ['Silver'] * 1
    # player_info.deck = ['Copper'] * 7 + ['Estate'] * 3 + ['Smithy'] * 1+ ['Silver'] * 1
    # player_info.deck = ['Copper'] * 7 + ['Estate'] * 3 + ['Smithy'] * 1+ ['Silver'] * 2
    # player_info.deck = ['Copper'] * 7 + ['Estate'] * 5 + ['Smithy'] * 1+ ['Silver'] * 1 + ['Festival'] * 1 + ['Gold']*5
    # print player_info.deck
    # player_info.bank = {'Copper': 10,
    #                     'Silver':30,
    #                     'Gold':10,
    #                     'Festival': 10,
    #                     'Laboratory': 10,
    #                     'Market': 10,
    #                     'Smithy':10,
    #                     'Village':10,
    #                    }
    # player_info.treasure = 6

    d = Domyon()
    #d = Domyon(card_dict)
    
    #print d.hand_value(player_info, ['Smithy'])

    #print d.avg_hand_value(player_info, [cc.Gold(), cc.Gold()])
    #print d.deck_value(player_info, [cc.Gold(), cc.Gold()])

    print d.buy_choice(player_info)

    #print d.deck_value(player_info)
    #print d.deck_value(player_info, [cc.Copper()])
    #print d.deck_value(player_info, [cc.Silver()])
    #print d.deck_value(player_info, [cc.Gold()])



if __name__ == '__main__':
    main()
