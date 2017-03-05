# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 23:41:51 2017

@author: xa
"""

import os
import game


class Item(game.object.Object):
    def __init__(self, nar, uid, data):
        keys = data.keys()

        for key in keys:
            if key.startswith('reply@'):
                data.pop(key)

        super().__init__(nar, uid, data)


class ItemReceiver(game.object.Object):
    def __init__(self, nar, uid, data):
        keys = data.keys()

        for key in keys:
            if key.startswith('reply@'):
                data.pop(key)
            elif key == 'activate_on':
                data.pop(key)

        super().__init__(nar, uid, data)

if __name__ == '__main__':
    game.registry.register_object_classes(game.object.Object)

    nar = game.narrator.Narrator()
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    game.state.load(nar, data_path, 'test_0.yaml')

    commands = """
        look inventory
        look
        look robot
        look rabbit
        touch first rabbit
        look second rabbit
    """

    for cmd in commands.split('\n'):
        nar.interact(cmd.strip())

    print(nar.state().current_room().dump())
    print(nar.state().current_room().get_by_uid('bowser').name().variants())
