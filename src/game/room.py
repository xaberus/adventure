# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:25:01 2017

@author: xa
"""


import collections
import game.dictionary
from game.object import Object, Container
from game.reply import Reply


def collect(d, k, v):
    if k not in d:
        d[k] = []
    a = d[k]
    if v not in a:
        a.append(v)


class Room(Object):
    _description = '{{ object | namdefl | cap }} was empty.'

    def __init__(self, nar, uid, data):
        objects = data.pop('objects', None)
        doors = data.pop('doors', None)
        description = data.pop('description', None)
        locations = data.pop('locations', {})

        super().__init__(nar, uid, data)

        self._locations = collections.OrderedDict()
        for loc_id, loc_data in locations.items():
            self._locations[loc_id] = loc_data.create(nar)

        self._objects = Container([self])
        self._doors = Container()

        if description is not None:
            self._description = description

        common = (
            '\n'
            '{% if objects | length > 0 %}'
            '<common>'
            '{% endif %}'
            '{% if doors | length > 0 %}{% for pos, door in doors.items() %}'
            '\n  {{ pos }}'
            ' you saw {{ door | namdefl | brk }}'
            '{% endfor %}{% endif %}'
        )

        if isinstance(self._description, list):
            look_replies = Reply([
                description + common
                for description in self._description
            ])
        else:
            look_replies = [self._description + common]

        self._arm.add_action_reply('reply@look', look_replies)

        if objects is not None:
            for obj_data in objects:
                obj = obj_data.create(nar, room=self)
                self.add_object(obj)

        if doors is not None:
            for door_data in doors:
                door = door_data.create(nar, room=self)
                self.add_door(door)

    def dump(self, level=0):
        out = []
        i = '  ' * level
        out.append(i + repr(self))

        out.append(i + '  objects:')
        for _, obj in self._objects.items():
            out.append(obj.dump(level + 2))
        out.append(i + '  doors:')
        for _, obj in self._doors.items():
            out.append(obj.dump(level + 2))

        return '\n'.join(out)

    def add_object(self, o):
        o.set_parent(self)
        self._objects.add(o)

    def remove_object(self, obj):
        self._objects.pop(obj)

    def add_door(self, d):
        d.set_parent(self)
        self._doors.add(d)

    def get_location(self, loc_id):
        if loc_id == 'room':
            return self._location
        else:
            return self._locations[loc_id]

    def find(self, idn):
        try:
            return self._objects.find(idn)
        except KeyError:
            return self._doors.find(idn)

    def get_by_uid(self, uid):
        try:
            return self._objects.get_by_uid(uid)
        except KeyError:
            return self._doors.get_by_uid(uid)

    def interact(self, action, target=None):
        if target is None:
            super().interact(action)
            return

        raise RuntimeError('not implemented yet')

    def extra_data(self, data):
        data['description'] = self._description
        # TODO: fill in dicovered objects
        # data['objects'] = {}
        data['room'] = self
        data['doors'] = {
            door.location().point_to(data): door
            for door in self._doors.values()
        }
