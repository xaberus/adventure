# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:25:01 2017

@author: xa
"""


from game.object import Object, Container
from game.reply import Reply


def collect(d, k, v):
    if k not in d:
        d[k] = []
    a = d[k]
    if v not in a:
        a.append(v)


class Room(Object):
    description = 'The {{ object | obj }} was empty.'
    point_preposition = 'in'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.objects = Container([self])
        self.doors = Container()
        self.object_map = {}

        self.common = (
            '\n'
            '{% if objects | length > 0 %}'
            '<common>'
            '{% endif %}'
            '{% if doors | length > 0 %}{% for pos, door in doors.items() %}'
            '\n  {{ pos }}'
            ' you saw {{ door | obj | a }}'
            ' {{ door | obj }}'
            '{% endfor %}{% endif %}'
        )

        if isinstance(self.description, list):
            self.look_replies = Reply([
                description + self.common
                for description in self.description
            ])
        else:
            self.look_replies = Reply([self.description + self.common])

        self.actions['look'] = self.look

    def name(self):
        return 'room'

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
        data['description'] = self.description
        data['objects'] = {}
        data['doors'] = {
            door.pred.point_in_room(self): door
            for door in self.doors.values()
        }
        raise self.look_replies.narrate(data)

    def remove_object(self, obj):
        self.objects.pop(obj)
