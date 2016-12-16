from __future__ import division

import sys
import inspect
from collections import defaultdict

import card_classes as cc
from game_play import Player


class Domyon(object):
    def __init__(self, card_dict):
        self.card_dict = card_dict

    def action_choice(self, player_info):
        if 'Laboratory' in player_info.actions_available:
            return 'Laboratory'
        elif 'Smithy' in player_info.actions_available:
            return 'Smithy'

    def buy_choice(self, player_info):
        available_cards = player_info.bank.keys()

        average_scores = defaultdict(int)
        average_scores[None] = self.avg_hand_value(player_info)[1]
        for c in available_cards:
            average_scores[c] = self.avg_hand_value(player_info,
                                                    [c])[1]
        print average_scores
        return max(average_scores.iterkeys(), key=(lambda key: average_scores[key]))

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
            scores[self.hand_value(player_info, cards)] += 1
        return scores, sum(k*v for k,v in scores.iteritems()) / sum(v for v in scores.values())

    def hand_value(self, player_info, cards=None):
        p = Player()
        p.discard = [x for x in player_info.deck]
        if cards:
            p.discard += cards
        p.draw_cards(5)

        p.actions_remaining = 1

        while p.actions_remaining > 0:
            p.actions_available = [x for x in p.hand if self.card_dict[x].grouping == 'Action']
            action = self.action_choice(p)
            if not action:
                break
            action = self.card_dict[self.action_choice(p)]
            player_info = self.update_player_info(p, action)

        total_val = 0
        total_val += sum([self.card_dict[x].treasure for x in p.hand if self.card_dict[x].grouping == 'Treasure'])
        #total_val += p.treasure

        return total_val

    def update_player_info(self, player_info, card):
        player_info.hand.remove(card.name)
        player_info.actions_remaining += -1 + card.gain_actions
        player_info.draw_cards(card.draw_cards)
        #player_info.buys += card.gain_buys
        #player_info.treasure += card.treasure
        return player_info



def get_card_dict():
    card_dict = {}
    for name, obj in inspect.getmembers(cc):
        if inspect.isclass(obj):
            card_dict[name] = obj()
    return card_dict

def main():
    card_dict = get_card_dict()

    player_info = Player()
    player_info.deck = ['Copper'] * 7 + ['Estate'] * 3
    player_info.bank = {"Smithy": 10, "Village": 10, 'Copper':30, 'Silver':30, 'Gold':5}
    player_info.bank = {'Silver':30, 'Gold':10, 'Smithy':30, 'Copper':10}
    player_info.treasure = 5

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
