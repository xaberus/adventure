# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 23:43:09 2017

@author: xa
"""

import game.dictionary
from game.object import Object
from game.name import ObjectName


class Door(Object):
    def __init__(self, nar, uid, data):
        if 'name' not in data:
            data['name'] = ObjectName(game.dictionary.nouns['door'])
        if 'location' not in data:
            data['location'] = None

        super().__init__(nar, uid, data)
