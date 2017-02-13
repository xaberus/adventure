# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:22:40 2017

@author: xa
"""

import jinja2
import game.verb
import game.action
from game.environment import env
from game.reply import Reply, RandomReply


class Narrator:
    def __init__(self):
        self.narratives = {}
        self.env = env
        self.room = None

        self.not_unique_reply = Reply([
            'There were more than one'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}'
            ' in the {{ room | predobj }}.'
            ' Did you mean{% for target in targets[:-1] %}'
            ' the'
            ' {{ target| predobj }}'
            '{%endfor%}'
            '{% for target in targets[-1:] %}'
            ' or the'
            ' {{ target| predobj }}'
            '{%endfor%}'
        ])

        self.no_target_reply = Reply([
            'Your call for {{ verb| ing }} was fruitless,'
            ' as it was missing a target.'
        ])

        self.target_not_found_reply = RandomReply([
            'You tried to {{ verb| inf }} {{ verb | prep }} the'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}'
            '. It was not there. You cried in desperation.',
            'In your head'
            ' {{ verb| inf }} {{ verb | prep }} the'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}'
            ' sounded particularly nice, but as soon as you tried to'
            ' say it aloud, it suddenly lost any sense.'
        ])

    def enter(self, room):
        self.room = room

    def parse(self, l):
        l = l.lower()
        tokens = l.split()

        if self.room is None:
            raise KeyError('no room')
        if len(tokens) >= 2:
            try:
                verb = game.verb.verbs[tokens[0]]
            except KeyError:
                self.invalid_verb_reply.complain(self, {
                    'verb': tokens[0],
                    'target': tokens[1:],
                })
                return

            try:
                target = self.room.find(tuple(tokens[1:]))
            except KeyError:
                self.target_not_found_reply.complain(self, {
                    'verb': verb,
                    'tokens': tokens[1:],
                })
                return
            if len(target) > 1:
                self.not_unique_reply.complain(self, {
                    'verb': verb,
                    'tokens': tokens[1:],
                    'targets': target,
                    'room': self.room,
                })
                return
        else:
            try:
                verb = game.verb.verbs[tokens[0]]
            except KeyError:
                self.invalid_verb_reply.complain(self, {
                    'verb': tokens[0],
                    'target': tokens[1:]
                })
                return

            return verb, self.room

        return verb, target[0]

    def interact(self, l):
        print('> {}'.format(l))
        t = self.parse(l)
        if t:
            verb, target = t
            action = game.action.actions[verb.base]

            target.interact(self, action)

    def say(self, msg):
        if len(msg) > 0:
            print(msg)

    def narrate(self, msg):
        if len(msg) > 0:
            print(msg)

    def complain(self, msg):
        if len(msg) > 0:
            print(msg)

    def get_narrative(self, narrative_id):
        if narrative_id not in self.narratives:
            self.narratives[narrative_id] = {}
        return self.narratives[narrative_id]
