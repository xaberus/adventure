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
    unknown_replies = RandomReply([
        'You did not knew how to {{ action | inf }}'
        ' {{ object | predobj }}'
        '{% if item %}'
        '{% if action | xprep %} {{ action | xprep }}{% endif %}'
        ' {{ item | predobj }}'
        '{% endif %}'
        '.',
        'You contemplated {{ action | ing }}'
        ' the {{ object | obj }}'
        '{% if item %}'
        '{% if action | xprep %} {{ action | xprep }}{% endif %}'
        ' {{ item | predobj }}'
        '{% endif %},'
        ' but you quickly changed your mind.',
        'At that point in time {{ action | ing }}'
        ' {{ object | predobj }}'
        '{% if item %}'
        '{% if action | xprep %} {{ action | xprep }}{% endif %}'
        ' {{ item | predobj }}'
        '{% endif %}'
        ' made no sense to you.'
    ])

    def __init__(self, nar, uid, pred=None):
        self.nar = nar
        self.uid = uid
        self.state = self.nar.require_uid_state(self.uid)
        self.actions = {}
        self.pred = pred
        self.parent = None

    def proper_name(self):
        return False

    def name(self):
        return 'object'

    def short_name(self):
        return self.name()

    def __repr__(self):
        n = self.name()
        sn = self.short_name()
        if n != sn:
            return '<{} a.k.a. {}>'.format(sn, n)
        else:
            return '<{}>'.format(sn, n)

    def set_parent(self, parent):
        if self.parent is not None:
            self.parent.remove_object(self)
        self.parent = parent

    def interact(self, action):
        data = {
            'action': action,
            'object': self,
            'item': action.predicate,
        }

        base = action.base
        if base not in self.actions:
            raise self.unknown_replies.complain(data)
        else:
            act = self.actions[base]
            if isinstance(act, Reply):
                raise act.say(data)
            else:
                try:
                    act(data)
                except InvalidInteraction as e:
                    raise self.unknown_replies.complain(data)


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
        return self.objects.__getitem__(key)

    def __missing__(self, key):
        return self.objects.__missing__(key)

    def __iter__(self):
        return self.objects.__iter__()

    def find(self, idn):
        return self.map[idn]

    def add(self, obj):
        self.objects[obj.uid] = obj
        self._register_objects()

    def pop(self, obj):
        self.objects.pop(obj.uid)
        self._register_objects()

    def values(self):
        return self.objects.values()
