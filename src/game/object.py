# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:28:42 2017

@author: xa
"""

from game.reply import RandomReply


class Object:
    def __init__(self, pred=None):
        self.actions = {}
        self.pred = pred

        self.unknown_replies = RandomReply([
            'You did not knew how to {{ verb | inf }}'
            ' the {{ object | obj }}.',
            'You contemplated about {{ verb | ing }}'
            ' the {{ object | obj }},'
            ' but you quickly changed your mind.',
            'At that point in time {{ verb | ing }}'
            ' the {{ object | obj }}'
            ' made no sense to you.'
        ])

    def name(self):
        return 'object'

    def __repr__(self):
        return '<{}>'.format(self.name())

    def short_name(self):
        return self.name()

    def interact(self, nar, action):
        data = {
            'action': action,
            'verb': action.verb,
            'object': self,
        }

        base = action.base
        if base not in self.actions:
            self.unknown_replies.say(nar, data)
        else:
            self.actions[base](nar, data)
