# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 23:41:51 2017

@author: xa
"""

import os
import game

if __name__ == '__main__':
    nar = game.narrator.Narrator()
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    game.state.load(nar, data_path, 'test_0.yaml')

    print(nar.state().current_room().dump())
    print(nar.state().inventory().dump())

    commands = """
#        look rabbit
#        look inventory
#        pet first rabbit
#        give long carrot to bowser
#        look inventory
#        give carrot to bowser
#        give carrot to cooper
#        look inventory
#        go through door
#

#        look

#        look inventory
#        look stubby carrot
#        take stubby carrot
#        take stubby carrot
#        look inventory
#        use long carrot and cooper

#        look door
#        close door
#        close door
#        open door
#        open door
#        look door

    #touch cooper
    #pet cooperb

    look computer
    look god
    look natascha
    touch natascha

    """

    for cmd in commands.split('\n'):
        nar.interact(cmd.strip())
