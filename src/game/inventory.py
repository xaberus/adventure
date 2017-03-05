# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 12:58:29 2017

@author: xa
"""

from game.name import ObjectName
from game.location import Location
from game.object import Container
from game.room import Room
from game.reply import Reply
import game.dictionary


class Inventory(Room):

    inventory_empty_replies = Reply([
        '{{ object | namdefl }} was empty.'
    ])

    inventory_replies = Reply([
        'In {{ object | namdefl | brk }} you saw:'
        '\n'
        '{% for item in objects %}'
        '  - {{ item | namindef }}'
        '{% if not loop.last %}\n{% endif %}'
        '{% endfor %}'
    ])

    def __init__(self, nar, uid, data):
        name = game.name.create({
            'noun': 'inventory',
            'predicates': [
                {'kind': 'pronoun', 'word': 'your'}
            ]
        })
        data['name'] = name
        data['location'] = Location({
            'name': name,
            'point_to': "in your inventory"
        })

        objects = data.pop('objects', None)

        super().__init__(nar, uid, data)

        self._objects = Container([self])

        if objects is not None:
            for obj_data in objects:
                obj_data['location'] = self._location
                obj = obj_data.create(nar, room=self)
                self.add_object(obj)

        self.actions['look'] = self.look

    def __repr__(self):
        out = []
        for item in self.objects:
            out.append(str(item))
        return '<inventory [{}]>'.format(', '.join(out))

    def look(self, data):
        if len(self.objects) == 0:
            raise self.inventory_empty_replies.say(data)

        data['objects'] = self.objects.values()

        raise self.inventory_replies.say(data)

    def add_object(self, o):
        o.set_parent(self)
        self.objects.add(o)

    def remove_object(self, obj):
        self.objects.pop(obj)

    def find(self, idn):
        return self.objects.find(idn)

    def interact(self, action, target=None):
        if target is None:
            super().interact(action)
            return

        raise RuntimeError('not implemented yet')
