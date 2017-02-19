# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:27:10 2017

@author: xa
"""

from game.predicate import Predicate
from game.room import Room
from game.doors import Door, MetalDoor
from game.object import Object
from game.reply import Reply
from game.narrator import Narrator


class Balkony(Room):
    description = (
        'You saw just a regular {{ object | obj }}.'
    )

    def name(self):
        return 'balkony'


class Carrot(Object):
    def __init__(self, *args, name=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.look_replies = Reply([
            'The {{ object | obj }} was fresh and looked tasty.'
            ' At least if you were a hare or a rabbit.'
        ])
        self.actions['look'] = self.look_replies

    def name(self):
        return 'carrot'

    def proper_name(self):
        return False

class Rabbit(Object):
    def __init__(self, *args, name=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.named = name

        self.state['rabbit'] = 'hungry'

        self.touch_replies = Reply([
            '{{ object | obj }} was warm and fluffy to the'
            ' {{ verb | inf }}.'
        ])
        self.actions['touch'] = self.touch_replies

        self.look_hungry_replies = Reply([
            'You mixed somehing up. {{ object | obj }} was looking at you.'
            ' You.'
            ' It wanted to be fed.'
        ])
        self.look_fed_replies = Reply([
            '{{ object | obj }} was fed and happy. It did not need you'
            ' anymore.'
        ])
        self.actions['look'] = self.look

        self.speak_replies = Reply([
            'You {{ verb | past }} {{ object | obj }}. You heared silence.'
            ' What did you expect?'
        ])
        self.actions['speak'] = self.speak_replies

    def name(self):
        return self.named

    def short_name(self):
        return 'rabbit'

    def proper_name(self):
        return True

    def look(self, data):
        if self.state['rabbit'] == 'hungry':
            self.look_hungry_replies.say(self.nar, data)
        else:
            self.look_fed_replies.say(self.nar, data)


if __name__ == '__main__':

    nar = Narrator()

    r = Balkony(nar, 'room001')
    nar.inventory_add_object(Carrot(nar, 'carrot'))
    r.add_object(Rabbit(nar, 'bowser', name='bowser'))
    r.add_object(Rabbit(nar, 'cooper', name='cooper'))
    r.add_door(Door(nar, 'door003', pred=Predicate('left')))
    nar.enter(r)

#    nar.interact('behold carrot')
#    nar.interact('look')
#
#    nar.interact('behold left door')
#    nar.interact('behold left door')
#    nar.interact('behold left door')
#    nar.interact('behold left door')

#    nar.interact('look rabbits')

    nar.interact('foo')
    nar.interact('look at car')

    nar.interact('look at left door')
    nar.interact('use left door')
    nar.interact('use carrot with bowser')
    
#    nar.interact('look rabbit')
#    nar.interact('touch bowser')
#    nar.interact('look bowser')
#    nar.require_uid_state('bowser')['rabbit'] = 'fed'
#    nar.interact('look bowser')
#    nar.interact('speak bowser')
#
#    nar.interact('use carrot on rabbit')

#    nar.interact('speak left door')


#    nar.interact('behold door')
#    nar.interact('behold left door')
#    nar.interact('behold right door')
#    nar.interact('behold left door')
#    nar.interact('behold left door')
#    nar.interact('behold left door')
#    nar.interact('open left door')
#    nar.interact('open metal door')
#    nar.interact('behold metal door')
#    nar.interact('behold')
#    nar.interact('behold left door')
#    nar.interact('behold left door')
#    nar.interact('behold left door')
