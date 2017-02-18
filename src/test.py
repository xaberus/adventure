# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:27:10 2017

@author: xa
"""

from game.predicate import Predicate
from game.room import Room
from game.doors import Door, MetalDoor
from game.narrator import Narrator
import game.action as action



if __name__ == '__main__':

    nar = Narrator()

    look_action = action.parse('look')
    open_action = action.parse('open')
    close_action = action.parse('close')
    speak_action = action.parse('speak')
    talk_action = action.parse('talk')
    touch_action = action.parse('touch')

    r = Room(nar, 'room001')
    r.add_door(Door(nar, 'door001', pred=Predicate('left')))
    r.add_door(MetalDoor(nar, 'door002', pred=Predicate('right')))
    r.add_door(MetalDoor(nar, 'door003', pred=Predicate('front')))
    nar.enter(r)
    nar.interact('behold door')
    nar.interact('behold left door')
    nar.interact('behold right door')
    nar.interact('behold left door')
    nar.interact('behold left door')
    nar.interact('behold left door')
    nar.interact('open left door')
    nar.interact('open metal door')
    nar.interact('behold metal door')
    nar.interact('behold')
    nar.interact('behold left door')
    nar.interact('behold left door')
    nar.interact('behold left door')
