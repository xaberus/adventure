# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 12:58:29 2017

@author: xa
"""

from game.location import Location
from game.object import Object, Container
import game.dictionary


class Inventory(Object):

    inventory_replies = [
        '{% if not object.is_empty() %}'
        'In {{ object | namdefl | brk }} you saw:'
        '\n'
        '{% for item in object.objects() %}'
        '  - {{ item | namindef }}'
        '{% if not loop.last %}\n{% endif %}'
        '{% endfor %}'
        '{% else %}'
        '{{ object | namdefl | cap | brk }} was empty.'
        '{% endif %}'
    ]

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

        self._arm.add_action_reply('reply@look',
                                   self.inventory_replies)

    def __repr__(self):
        cn = self.__class__.__name__
        out = []
        for item in self._objects:
            out.append(str(item))
        return '{}<[{}]>'.format(cn, ', '.join(out))

    def dump(self, level=0):
        out = []
        i = '  ' * level
        out.append(i + self.__class__.__name__)

        out.append(i + '  objects:')
        for _, obj in self._objects.items():
            out.append(obj.dump(level + 2))

        return '\n'.join(out)

    def add_object(self, o):
        o.set_parent(self)
        self._objects.add(o)

    def remove_object(self, obj):
        self._objects.pop(obj)

    def is_empty(self):
        return len(self._objects) == 0

    def objects(self):
        return self._objects.values()

    def find(self, idn):
        return self._objects.find(idn)

    def interact(self, action, target=None):
        if target is None:
            super().interact(action)
            return

        raise RuntimeError('not implemented yet')
