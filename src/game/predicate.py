# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 14:37:50 2017

@author: xa
"""

from game.environment import env

to_the_templ = env.from_string('to the {{ pred | upper }}'
                               ' of the {{ room | obj }}')
in_the_templ = env.from_string('in the {{ pred | upper }}'
                               ' of the {{ room | obj }}')


class Predicate:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

    def point_in_room(self, room):
        data = {
            'pred': self._name,
            'room': room,
        }
        if self._name in ('left', 'right'):
            return to_the_templ.render(data)
        elif self._name in ('front', 'back'):
            return in_the_templ.render(data)
        else:
            raise NotImplementedError()
