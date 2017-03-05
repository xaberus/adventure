# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:25:01 2017

@author: xa
"""


import game.dictionary
from game.object import Object, Container
from game.reply import Reply
from game.name import ObjectName
from game.location import Location


def collect(d, k, v):
    if k not in d:
        d[k] = []
    a = d[k]
    if v not in a:
        a.append(v)


class Room(Object):
    _description = '{{ object | namdefl | cap }} was empty.'

    def __init__(self, nar, uid, **kwargs):
        objects = kwargs.pop('objects', None)
        doors = kwargs.pop('doors', None)
        description = kwargs.pop('description', None)

        super().__init__(nar, uid, **kwargs)

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
            ' you saw {{ door | namdefl }}'
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
            for obj_uid, obj in objects.items():
                self.add_object(game.object.create(nar, obj_uid, obj))

        if doors is not None:
            for door_uid, door in doors.items():
                self.add_door(game.object.create(nar, door_uid, door))

    def add_object(self, o):
        o.set_parent(self)
        self.objects.add(o)

    def add_door(self, d):
        d.set_parent(self)
        self.doors.add(d)

    def find(self, idn):
        try:
            return self.objects.find(idn)
        except KeyError:
            return self.doors.find(idn)

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
        print(data['doors'])
        raise self.look_replies.narrate(data)

    def remove_object(self, obj):
        self.objects.pop(obj)
