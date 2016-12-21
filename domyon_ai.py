from __future__ import division

import sys
sys.dont_write_bytecode = True
import inspect
from collections import defaultdict

import card_classes as cc
from game_play import Player

'''To Implement Notes

ACTION
- Highest inc in expected value
- Need Differences between 1 action remaining and two actions remaining

VICTORY
- Can calculate Probabilities of getting an 8 vs opponent probaiblity getting an 8. Then from there can decide when to start buying.


'''

class Domyon(object):
    def __init__(self, card_dict):
        self.card_dict = card_dict

    def action_choice(self, player_info):
    #First, look for any card that provides additional actions, order not as important currently 
        for c in player_info.actions_available:
            if self.card_dict[c].gain_actions >= 1:
                return c
        #Otherwise, play card that give best expected value
        #Should consider number of remaining actions, if 2+ perhaps plays smithy to have chance of more actions
        #if not, simple best next card

        if 'Smithy' in player_info.actions_available:
            return 'Smithy'

    def buy_choice(self, player_info):
        available_cards = list(filter(lambda x: self.card_dict[x].cost <= player_info.treasure, 
                                      player_info.bank.keys()))

        average_scores = defaultdict(int)
        GT5 = defaultdict(int)
        GT8 = defaultdict(int)
        scores = self.avg_hand_value(player_info)
        average_scores[None] = self.calc_avg_score(scores)
        GT5[None] = self.calc_gt_x(scores, 5)
        GT8[None] = self.calc_gt_x(scores, 8)

        for c in available_cards:
            scores = self.avg_hand_value(player_info, [c])
            average_scores[c] = self.calc_avg_score(scores)
            GT5[c] = self.calc_gt_x(scores, 5)
            GT8[c] = self.calc_gt_x(scores, 8)

        self.pretty_print_dict(average_scores, 'Average Scores') 
        self.pretty_print_dict(GT5, 'Greater Than Five:') 
        self.pretty_print_dict(GT8, 'Greater Than Eight') 
        return max(average_scores.iterkeys(), key=(lambda key: average_scores[key]))

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

    def avg_hand_value(self, player_info, cards=None, its = 5000):
        scores = defaultdict(int)
        for x in xrange(its):
            p = Player()
            p.discard = [x for x in player_info.deck]
            p.deck = []
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
            action = self.action_choice(p)
            if not action:
                break
            action = self.card_dict[self.action_choice(p)]
            p = self.update_player(p, action)

        total_val = 0
        total_val += sum([self.card_dict[x].treasure for x in p.hand if self.card_dict[x].grouping == 'Treasure'])
        total_val += p.treasure

        return total_val

    def update_player(self, p, card):
        p.hand.remove(card.name)
        p.actions_remaining += -1 + card.gain_actions
        p.draw_cards(card.draw_cards)
        #p.buys += card.gain_buys
        p.treasure += card.gain_treasure
        return p

def get_card_dict():
    card_dict = {}
    for name, obj in inspect.getmembers(cc):
        if inspect.isclass(obj):
            card_dict[name] = obj()
    return card_dict

def main():
    card_dict = get_card_dict()

    player_info = Player()
    player_info.deck = ['Copper'] * 7 + ['Estate'] * 3 #+ ['Smithy'] * 1+ ['Silver'] * 1
    player_info.deck = ['Copper'] * 7 + ['Estate'] * 3 + ['Festival']# * 1+ ['Silver'] * 1
    player_info.deck = ['Copper'] * 7 + ['Estate'] * 3 + ['Smithy'] * 1+ ['Silver'] * 1
    player_info.deck = ['Copper'] * 7 + ['Estate'] * 3 + ['Smithy'] * 1+ ['Silver'] * 2
    player_info.deck = ['Copper'] * 7 + ['Estate'] * 5 + ['Smithy'] * 1+ ['Silver'] * 1 + ['Festival'] * 1 + ['Gold']*5
    print player_info.deck
    player_info.bank = {'Copper': 10,
                        'Silver':30,
                        'Gold':10,
                        'Festival': 10,
                        'Laboratory': 10,
                        'Market': 10,
                        'Smithy':10,
                        'Village':10,
                       }
    player_info.treasure = 6

    d = Domyon(card_dict)
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
