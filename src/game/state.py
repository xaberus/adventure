# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 13:14:26 2017

@author: xa
"""


import os
import re
import yaml
import pprint
import collections
import game.name
import game.location
import game.object
import game.room
import game.door
import game.inventory
import game.narrator
from game.util import debug


class Proto(collections.OrderedDict):
    def create(self, nar, room=None):
        raise NotImplementedError()

    def merge_data(self, m):
        if m is None:
            return

        def _merge(d, m):
            for k, v in m.items():
                if k in d:
                    if isinstance(d[k], dict):
                        _merge(d[k], v)
                    else:
                        d[k] = v
                else:
                    d[k] = v

        _merge(self, m)

    def __repr__(self):
        cn = self.__class__.__name__
        name = self.get('name')
        return '{}<{}>'.format(cn, name.default_form([]))


class LocationProto(Proto):
    def create(self, nar, room=None):
        return game.location.Location(self)


class ObjectProto(Proto):
    def create(self, nar, room=None):
        uid = self.pop('uid', None)
        if uid is None:
            name = self.get('name').simple_form([])
            uid = nar.state().next_uid(name)
        # pass room whete the object is instantiated
        self['room'] = room
        return game.object.create(nar, uid, self)


class InventoryProto(ObjectProto):
    pass


class RoomProto(ObjectProto):
    pass


class GameProto(Proto):
    def create(self, nar, room=None):
        State(nar, self)


class GameLoader(yaml.Loader):
    names = {
        'Bowser': {'name': 'Bowser'}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_constructor('!include', self._include)
        self.add_constructor('!Name', self._contruct_name)
        self.add_constructor('!Object', self._construct_object)
        self.add_constructor('!Location', self._construct_location)
        self.add_constructor('!Room', self._construct_room)
        self.add_constructor('!Inventory', self._construct_inventory)
        self.add_constructor('!Game', self._contruct_game)

    def _include(self, loader, node):
        try:
            m = loader.construct_mapping(node, deep=True)
            path = m.pop('path')
        except yaml.MarkedYAMLError:
            path = loader.construct_scalar(node)
            m = None

        file_path = os.path.join(self.data_path, path)
        data = yaml.load(open(file_path, 'r'), Loader=self.__class__)
        data.merge_data(m)
        return data

    def _contruct_name(self, loader, node):
        try:
            data = loader.construct_mapping(node, deep=True)
            name = game.name.create(data)
            return name
        except yaml.MarkedYAMLError:
            word = loader.construct_scalar(node)
            name = game.name.names[word]
            return name

    def _construct_location(self, loader, node):
        return LocationProto(loader.construct_pairs(node, deep=True))

    def _construct_object(self, loader, node):
        return ObjectProto(loader.construct_pairs(node, deep=True))

    def _construct_room(self, loader, node):
        return RoomProto(loader.construct_pairs(node, deep=True))

    def _construct_inventory(self, loader, node):
        return InventoryProto({
            'objects': loader.construct_sequence(node, deep=True)
        })

    def _contruct_game(self, loader, node):
        return GameProto(loader.construct_pairs(node, deep=True))


class State:
    def __init__(self, nar, data):
        self._nar = nar
        self._state = {}
        self._state['@narratives'] = {}
        self._narratives = self._state['@narratives']
        self._next_uid = 1
        self._current_room = None

        nar.set_state(self)

        rooms_data = data.pop('rooms')
        inventory_data = data.pop('inventory')
        current_room = data.pop('current_room')

        self._rooms = collections.OrderedDict()
        for room_data in rooms_data:
            room = room_data.create(nar)
            room_uid = room.uid()
            self._rooms[room_uid] = room

        self._inventory = game.inventory.Inventory(nar, 'inventory',
                                                   inventory_data)

        self.enter_room(current_room)

        for key in data:
            raise TypeError('got an unexpected argument: {}'.format(key))

    def __repr__(self):
        return pprint.pformat(self._state)

    def get_narrative(self, narrative_id):
        if narrative_id not in self._narratives:
            self._narratives[narrative_id] = {}
        return self._narratives[narrative_id]

    def next_uid(self, tmpl=None):
        if tmpl is None:
            tmpl = 'auto'
        else:
            tmpl = '_'.join(tmpl.split()).lower()
        n = self._next_uid
        self._next_uid += 1
        return '{}_{}'.format(tmpl, n)

    def require_uid_state(self, uid, state):
        if state is None:
            state = {}

        m = re.match('[a-z0-9_]+', uid)
        if m is None:
            raise KeyError('malformed uid {}'.format(uid))

        if uid not in self._state:
            self._state[uid] = state

        return self._state[uid]

    def inventory(self):
        return self._inventory

    def inventory_add_object(self, obj):
        self._inventory.add_object(obj)

    def inventory_find(self, idn):
        return self._inventory.find(idn)

    def enter_room(self, room):
        if isinstance(room, str):
            room = self._rooms[room]

        debug('[enter]', room)
        self._current_room = room

    def current_room(self):
        return self._current_room


def load(nar, data_path, level_name):
    class AugmentedGameLoader(GameLoader):
        data_path = None
        nar = None

    AugmentedGameLoader.data_path = data_path
    AugmentedGameLoader.nar = nar

    level_path = os.path.join(data_path, level_name)
    game_data = yaml.load(open(level_path, 'r'), Loader=AugmentedGameLoader)
    return game_data.create(nar)
