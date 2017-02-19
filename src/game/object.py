# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:28:42 2017

@author: xa
"""

import itertools
import collections
from game.reply import Reply, RandomReply
from game.util import collect


class InvalidInteraction(Exception):
    pass


class Object:
    def __init__(self, nar, uid, pred=None):
        self.nar = nar
        self.uid = uid
        self.state = self.nar.require_uid_state(self.uid)
        self.actions = {}
        self.pred = pred

        self.unknown_replies = RandomReply([
            'You did not knew how to {{ verb | inf }}'
            ' {{ object | predobj }}'
            '{% if item %}'
            '{% if verb | xprep %} {{ verb | xprep }}{% endif %}'
            ' {{ item | predobj }}'
            '{% endif %}'
            '.',
            'You contemplated {{ verb | ing }}'
            ' the {{ object | obj }}'
            '{% if item %}'
            '{% if verb | xprep %} {{ verb | xprep }}{% endif %}'
            ' {{ item | predobj }}'
            '{% endif %},'
            ' but you quickly changed your mind.',
            'At that point in time {{ verb | ing }}'
            ' {{ object | predobj }}'
            '{% if item %}'
            '{% if verb | xprep %} {{ verb | xprep }}{% endif %}'
            ' {{ item | predobj }}'
            '{% endif %}'
            ' made no sense to you.'
        ])

    def proper_name(self):
        return False

    def name(self):
        return 'object'

    def __repr__(self):
        return '<{}>'.format(self.name())

    def short_name(self):
        return self.name()

    def interact(self, action, item=None):
        data = {
            'action': action,
            'verb': action.verb,
            'object': self,
            'item': item,
        }

        base = action.base
        if base not in self.actions:
            self.unknown_replies.say(self.nar, data)
        else:
            act = self.actions[base]
            if isinstance(act, Reply):
                act.say(self.nar, data)
            else:
                act(data)


class Container():
    def __init__(self, extra=[]):
        self.extra = extra
        self.objects = collections.OrderedDict()
        self.map = {}

    def _register_objects(self):
        self.map = {}

        for obj in itertools.chain(self.objects.values(), self.extra):
            idn = tuple(obj.name().split())
            collect(self.map, idn, obj)
            idn = tuple(obj.short_name().split())
            collect(self.map, idn, obj)
            pred = obj.pred
            if pred is not None:
                idn = tuple([obj.pred.name()] + obj.name().split())
                collect(self.map, idn, obj)
                idn = tuple([obj.pred.name()] + obj.short_name().split())
                collect(self.map, idn, obj)

    def __len__(self):
        return self.objects.__len__()

    def __getitem__(self, key):
        return self.map.__getitem__(key)

    def add(self, obj):
        self.objects[obj.uid] = obj
        self._register_objects()
