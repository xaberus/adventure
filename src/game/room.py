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

        self.objects = Container([self])
        self.doors = Container()

        if description is not None:
            self._description = description

        self.common = (
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
            self.look_replies = Reply([
                description + self.common
                for description in self._description
            ])
        else:
            self.look_replies = Reply([self._description + self.common])

        self.actions['look'] = self.look

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
        for _, obj in self.objects.items():
            out.append(obj.dump(level + 2))
        out.append(i + '  doors:')
        for _, obj in self.doors.items():
            out.append(obj.dump(level + 2))

        return '\n'.join(out)

    def add_object(self, o):
        o.set_parent(self)
        self.objects.add(o)

    def remove_object(self, obj):
        self.objects.pop(obj)

    def add_door(self, d):
        d.set_parent(self)
        self.doors.add(d)

    def get_location(self, loc_id):
        if loc_id == 'room':
            return self._location
        else:
            return self._locations[loc_id]

    def find(self, idn):
        try:
            return self.objects.find(idn)
        except KeyError:
            return self.doors.find(idn)

    def get_by_uid(self, uid):
        try:
            return self.objects.get_by_uid(uid)
        except KeyError:
            return self.doors.get_by_uid(uid)

    def interact(self, action, target=None):
        if target is None:
            super().interact(action)
            return

        raise RuntimeError('not implemented yet')

    def look(self, data):
        data['description'] = self._description
        data['objects'] = {}
        data['room'] = self
        data['doors'] = {
            door.location().point_to(data): door
            for door in self.doors.values()
        }
        raise self.look_replies.narrate(data)
