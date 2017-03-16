# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 23:43:09 2017

@author: xa
"""

from game.object import Object


class Door(Object):
    def __init__(self, nar, uid, data):
        self.destination = data.pop('destination')
        super().__init__(nar, uid, data)

    def enter(self):
        self._nar.enter(self.destination)
