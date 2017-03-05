# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 23:41:51 2017

@author: xa
"""

import os
import game

class Item(game.object.Object):
    pass


class ItemReceiver(game.object.Object):
    def __init__(self, nar, uid, data):
        super().__init__(nar, uid, data)

        self.objects = set()

    def add_object(self, o):
        o.set_parent(self, relocate=True)
        self.objects.add(o)

    def remove_object(self, obj):
        self.objects.remove(obj)


if __name__ == '__main__':
    game.registry.register_object_classes(game.object.Object)

    nar = game.narrator.Narrator()
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    game.state.load(nar, data_path, 'test_0.yaml')

    """
        look inventory
        look
        look robot
        look rabbit
        look long carrot
        touch first rabbit
        look second rabbit
        look second rabbit
        pet second rabbit

        give long carrot to bowser

        look inventory
        pet first rabbit
        give long carrot to bowser
        look inventory
        give carrot to bowser
        give carrot to cooper
        look inventory
        go through door
    """

    commands = """
        look door
    """


    for cmd in commands.split('\n'):
        nar.interact(cmd.strip())


