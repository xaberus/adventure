# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 09:13:00 2017

@author: xa
"""

import game.verb


class Action:
    def __init__(self, verb):
        self.verb = verb

    def __format__(self, spec):
        return self.verb.__format__(spec)


class Look(Action):
    base = 'look'


class Open(Action):
    base = 'open'


class Close(Action):
    base = 'close'


class Take(Action):
    base = 'take'


class Use(Action):
    base = 'use'


class Go(Action):
    base = 'go'


class Speak(Action):
    base = 'speak'


class Touch(Action):
    base = 'touch'


actions_map = {
    'look': Look,
    'behold': Look,
    'open': Open,
    'close': Close,
    'take': Take,
    'use': Use,
    'go': Go,
    'speak': Speak,
    'talk': Speak,
    'touch': Touch,
}

actions = {
    base: actions_map[base](verb)
    for base, verb in game.verb.verbs.items()
}


def parse(base):
    return actions[base]
