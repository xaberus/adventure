#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 13:20:55 2017

@author: xa
"""

from game.environment import env
import game.name


class Location():
    def __init__(self, **kwargs):
        name = kwargs.pop('name', None)
        if name is None:
            raise TypeError('location has no name')
        self._name = game.name.create(name)

        point_to = kwargs.pop('point_to', None)
        if point_to is None:
            raise TypeError('location has no point_to')
        self._point_to = env.from_string(point_to)

    def name(self):
        return self._name

    def point_to(self, data):
        return self._point_to.render(data)

    def __repr__(self):
        out = self._name.default_form([])
        return 'Location<{}>'.format(out)


def create(loc):
    if not isinstance(loc, dict):
        return loc

    return Location(**loc)
