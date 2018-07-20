import os
import itertools
from ConfigParser import ConfigParser

def InkcardsSetup(env, confFile='inkcards.conf'):
    # Replace with values from conf file.
    config = ConfigParser()
    config.read(os.path.join(str(confFile)))
    conf = config.defaults()
    env['svg_src'] = conf.get('svg_src', 'card_layers.svg')
    env['dest'] = conf.get('dest', 'card_set.pdf')

    # Remove the extensions if any, it'll be added by the builder.
    env['svg_src'] = os.path.splitext(env['svg_src'])[0]
    env['dest'] = os.path.splitext(env['dest'])[0]

    env['INKCARDS'] = config.sections()

def sortCardsToPrintBack(l, w):
    # Split a list of cards by w, reverse these lists and join them.
    splitedList = [l[i:i + w] for i in range(0, len(l), w)]
    reversedLists = [list(reversed(x)) for x in splitedList]
    return sum(reversedLists, [])

def unifyCardList(front, rear, w, h):
    l1 = [front[i:i + w*h] for i in range(0, len(front), w*h)]
    l2 = [rear [i:i + w*h] for i in range(0, len(rear ), w*h)]
    iters = [iter(l1), iter(l2)]
    return list(it.next() for it in itertools.cycle(iters))

