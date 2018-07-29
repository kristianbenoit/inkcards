import re
import os
from inkcards_utils import InkcardsSetup, sortCardsToPrintBack, unifyCardList

env = Environment(tools = ['Inkcards', 'Tiling'])
InkcardsSetup(env)

cards=[]
for cardName in env['INKCARDS']:
    card = {}
    card['front'] = env.Inkcards('%s-front'%cardName, env['svg_src'], CARD_NAME=cardName, CARD_SIDE='front')
    card['rear'] = env.Inkcards('%s-rear'%cardName, env['svg_src'], CARD_NAME=cardName, CARD_SIDE='rear')
    cards.append(card)

##########################
## Uncommented it create 3 PDFs
## - one for the front,
## - one for the back,
## - and a unified.
## But I found out that countersheet is there to offer such a feature.
#
#width=2
#height=4
#
#nbMissingCards = width*height - len(env['INKCARDS'])%(width*height)
#for i in range(0,nbMissingCards):
#    env['INKCARDS'].append
#
#front = [card['front'] for card in cards]
#frontSides = env.Tiling(env['dest'] + '-front', front, INKCARDS_ROT=90)
#
#rear = sortCardsToPrintBack([card['rear'] for card in cards], width)
#rearSides = env.Tiling(env['dest'] + '-rear', rear, INKCARDS_ROT=-90)
#
## This is a try to unify all cards, but need to be patched with empty cards.
## The rear must also be rotated 180 degrees to be printed correctly.
#final = unifyCardList(front, rear, width, height)
#sheets = env.Tiling(env['dest'], final, INKCARDS_ROT=90)
##############################
