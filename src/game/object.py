# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:28:42 2017

@author: xa
"""

import itertools
import collections
import game.registry
from game.reply import Reply, RandomReply
from game.util import collect
from game.util import debug


class InvalidInteraction(Exception):
    pass


class Object:
    unknown_replies = RandomReply([
        'You did not knew how to {{ action.verb | inf | brk }}'
        ' {{ object | namdefl | brk }}'
        '{% if item %}'
        '{% if action | xprep %} {{ action.verb | xprep | brk }}{% endif %}'
        ' {{ item | namdefl | brk }}{% endif %}.',

        'You contemplated {{ action.verb | ing | brk }}'
        ' {{ object | namdefl | brk }}'
        '{% if item %}'
        '{% if action | xprep %} {{ action.verb | xprep | brk }}{% endif %}'
        ' {{ item | namdefl | brk }}'
        '{% endif %},'
        ' but you quickly changed your mind.',

        'At that point in time {{ action.verb | ing | brk }}'
        ' {{ object | namdefl | brk }}'
        '{% if item %}'
        '{% if action | xprep %} {{ action | xprep | brk }}{% endif %}'
        ' {{ item | namdefl | brk }}'
        '{% endif %}'
        ' made no sense to you.'
    ])

    def __init__(self, nar, uid, data, room=None):
        self._nar = nar
        self._uid = uid

        self.parent = None

        name = data.pop('name', None)
        if name is None:
            raise TypeError('object has no name')
        assert isinstance(name, game.name.Name)
        self._name = name

        short_name = data.pop('short_name', None)
        if short_name is None:
            short_name = self._name
        assert isinstance(short_name, game.name.Name)
        self._short_name = short_name

        room = data.pop('room', None)

        location = data.pop('location', None)
        if location is None:
            raise TypeError('object {} has no location'.format(uid))
        if isinstance(location, str):
            self._location = room.get_location(location)
        else:
            self._location = location.create(self._nar)

        kind = data.pop('kind', None)
        if kind is None:
            kind = self._name.drop_predicates()
        assert isinstance(kind, game.name.Name)
        self._kind = kind

        state = data.pop('state', None)
        self._state = self._nar.state().require_uid_state(self._uid, state)

        activation_map = data.pop('activation_map', {})
        self._arm = game.actionutils.ActionReplyMap(self._state,
                                                    activation_map, self)

        keys = list(data.keys())
        for key in keys:
            if key.find('@') > 0:
                self._arm.add_action_reply(key, data.pop(key))

        for key in data:
            raise TypeError('got an unexpected argument: {}'.format(key))

    def uid(self):
        return self._uid

    def name(self):
        return self._name

    def short_name(self):
        return self._short_name

    def kind(self):
        return self._kind

    def location(self):
        return self._location

    def __repr__(self):
        cn = self.__class__.__name__
        n = self._name
        sn = self._short_name
        if n != sn:
            return '{}<{} a.k.a. {}>'.format(cn, sn, n)
        else:
            return '{}<{}>'.format(cn, sn, n)

    def dump(self, level=0):
        i = '  ' * level
        return i + repr(self)

    def set_parent(self, parent, relocate=False):
        if self.parent is not None:
            self.parent.remove_object(self)
        self.parent = parent
        if relocate:
            self._location = self.parent.location()

    def extra_data(self, data):
        return

    def interact(self, action):
        data = {
            'action': action,
            'object': self,
            'item': action.predicate,
            'inventory': self._nar.state().inventory(),
        }

        self.extra_data(data)

        try:
            self._arm.handle_action(action, data)
        except game.object.InvalidInteraction:
            raise self.unknown_replies.complain(data)


class Container():
    def __init__(self, extra=[]):
        self.extra = extra
        self.objects = collections.OrderedDict()
        self.map = {}

        self._register_objects()

    def _register_objects(self):
        self.map = {}

        for obj in itertools.chain(self.objects.values(), self.extra):
            variants = obj.name().variants()
            for idn in variants:
                collect(self.map, idn, obj)

            variants = obj.short_name().variants()
            for idn in variants:
                collect(self.map, idn, obj)

            variants = obj.kind().variants()
            for idn in variants:
                collect(self.map, idn, obj)

    def __len__(self):
        return self.objects.__len__()

    def __getitem__(self, key):
        return self.objects.__getitem__(key)

    def __missing__(self, key):
        return self.objects.__missing__(key)

    def __iter__(self):
        return self.objects.__iter__()

    def items(self):
        return self.objects.items()

    def find(self, idn):
        return self.map[idn]

    def get_by_uid(self, uid):
        return self.objects[uid]

    def add(self, obj):
        self.objects[obj.uid()] = obj
        self._register_objects()

    def pop(self, obj):
        self.objects.pop(obj.uid())
        self._register_objects()

    def values(self):
        return self.objects.values()


def create(nar, uid, obj_or_dict):
    debug('[load object]', obj_or_dict)
    if isinstance(obj_or_dict, dict):
        class_name = obj_or_dict.pop('class')
        cls = game.registry.object_classes[class_name]
        return cls(nar, uid, obj_or_dict)
    else:
        return obj_or_dict


class Item(Object):
    def take(self):
        self._nar.state().inventory_add_object(self)


class ItemReceiver(Object):
    def __init__(self, nar, uid, data):
        super().__init__(nar, uid, data)

        self.objects = set()

    def add_object(self, o):
        o.set_parent(self, relocate=True)
        self.objects.add(o)

    def remove_object(self, obj):
        self.objects.remove(obj)

    def extra_data(self, data):
        data['items'] = list(self.objects)
