___author__ = 'stevenkerr'
from domyon_ai import Domyon 

d = Domyon()


def action_choice(player_info):
    a = d.action_choice(player_info)
    # print 'Action: ', a
    return a

def execute_action_strategy(player_info, action):
    return d.execute_action_strategy(player_info, action)


def buy_choice(player_info):
    b = d.buy_choice(player_info)
    # print 'Buy: ', b
    return b