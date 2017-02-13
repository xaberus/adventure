# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 23:44:13 2017

@author: xa
"""

import itertools
import random

from game.environment import env


class Reply:
    def __init__(self, variants):
        self.set_variants(variants)

    def set_variants(self, variants):
        self.variants = [
            env.from_string(variant)
            for variant in variants
        ]
        self.cycle = None

    def choose_reply(self, nar, data):
        if self.cycle is None:
            self.cycle = itertools.cycle(self.variants)

        return next(self.cycle)

    def say(self, nar, data):
        v = self.choose_reply(nar, data)
        nar.say(v.render(data))

    def narrate(self, nar, data):
        v = self.choose_reply(nar, data)
        nar.narrate(v.render(data))

    def complain(self, nar, data):
        v = self.choose_reply(nar, data)
        nar.complain(v.render(data))


class RandomReply(Reply):
    def choose_reply(self, nar, data):
        def picker():
            while True:
                i = random.randint(0, len(self.variants) - 1)
                yield self.variants[i]
        if self.cycle is None:
            self.cycle = picker()

        return next(self.cycle)


class NarrativeReply(Reply):
    def __init__(self, narrative_id, variants, narrative):
        super().__init__(variants)

        self.narrative_id = narrative_id
        self.narrative = [
            env.from_string(variant)
            for variant in narrative
        ]

    def choose_reply(self, nar, data):
        if self.cycle is None:
            n = nar.get_narrative(self.narrative_id)
            if 'told' not in n:
                self.cycle = itertools.chain(self.variants, self.narrative)
            else:
                self.cycle = itertools.cycle(self.variants)

        try:
            v = next(self.cycle)
        except StopIteration:
            self.cycle = itertools.cycle(self.variants)
            v = next(self.cycle)
            nar.get_narrative(self.narrative_id)['told'] = True

        return v
