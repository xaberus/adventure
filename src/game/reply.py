# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 23:44:13 2017

@author: xa
"""

import itertools
import random

from game.environment import env


class NarratorMessage(Exception):
    def __init__(self, message):
        self.message = message


class NarratorNarration(NarratorMessage):
    pass


class NarratorAnswer(NarratorMessage):
    pass


class NarratorComplaint(NarratorMessage):
    pass


class Reply:
    def __init__(self, variants):
        self.set_variants(variants)

    def set_variants(self, variants):
        self.variants = [
            env.from_string(variant)
            for variant in variants
        ]
        self.cycle = None

    def choose_reply(self, data):
        if self.cycle is None:
            self.cycle = itertools.cycle(self.variants)

        return next(self.cycle)

    def say(self, data):
        v = self.choose_reply(data)
        return NarratorAnswer(v.render(data))

    def narrate(self, data):
        v = self.choose_reply(data)
        return NarratorNarration(v.render(data))

    def complain(self, data):
        v = self.choose_reply(data)
        return NarratorComplaint(v.render(data))


class RandomReply(Reply):
    def choose_reply(self, data):
        def picker():
            while True:
                i = random.randint(0, len(self.variants) - 1)
                yield self.variants[i]
        if self.cycle is None:
            self.cycle = picker()

        return next(self.cycle)


class NarrativeReply(Reply):
    def __init__(self, nar, narrative_id, variants, narrative):
        super().__init__(variants)

        self.narrative_id = narrative_id
        self.narrative = [
            env.from_string(variant)
            for variant in narrative
        ]
        self.narrate_state = nar.state().get_narrative(self.narrative_id)
        self.narrate_state['told'] = False

    def choose_reply(self, data):
        if self.cycle is None:
            if not self.narrate_state['told']:
                self.cycle = itertools.chain(self.variants, self.narrative)
            else:
                self.cycle = itertools.cycle(self.variants)

        try:
            v = next(self.cycle)
        except StopIteration:
            self.cycle = itertools.cycle(self.variants)
            v = next(self.cycle)
            self.narrate_state['told'] = True
        return v
