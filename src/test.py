# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:27:10 2017

@author: xa
"""

from game.predicate import Predicate
from game.room import Room
from game.doors import Door, MetalDoor
from game.object import InvalidInteraction, Object
from game.reply import Reply
from game.narrator import Narrator


class Balkony(Room):
    description = (
        'Your {{ object | obj }} looked like always.'
        ' A gentle rustle was the evidence of your two favorite rabbits:'
        ' Cooper and Boswer.'
    )
    point_preposition = 'on'

    def name(self):
        return 'balkony'


class Carrot(Object):
    def __init__(self, *args, name=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.look_replies = Reply([
            'The {{ object | obj }} was fresh and looked tasty.'
            ' At least if you were a hare or a rabbit.'
            ' For no aparent reason you knew that'
            ' this was {{ object | predobj }}.'
        ])
        self.actions['look'] = self.look_replies

    def name(self):
        return 'carrot'

    def proper_name(self):
        return False


class Rabbit(Object):
    touch_replies = Reply([
        '{{ object | obj }} was warm and fluffy to the'
        ' {{ action | inf }}.'
    ])

    look_hungry_replies = Reply([
        'You mixed somehing up. {{ object | obj }} was looking at you.'
        ' You.'
        ' It wanted to be fed.',
        '{{ object | obj }}, one of your favourite rabbits was looking at you.'
    ])
    look_fed_replies = Reply([
        '{{ object | obj }} was firmly holding {{ item | predobj }}'
        ' in its tiny paws. It looked happy and for a moment you'
        ' imagened to see a glimpse of gratitude in its eyes.',
        '{{ object | obj }} was fed and happy. Your attention was not '
        'needed anymore.'
    ])

    speak_replies = Reply([
        'You {{ action | past }} {{ object | obj }}. You heared silence.'
        ' What did you expect?'
    ])

    combine_carrot_replies = Reply([
        '{{ object | predobj }} snatched {{ item | predobj }} from'
        ' your hand.',
        'You gave {{ item | predobj }} to {{ object | predobj }}.'
        ' Silently you remarked something about order not having'
        ' a particular meaning.'
    ])
    combine_carrot_fed_replies = Reply([
        'You almost gave the {{ item | predobj }} to {{ object | predobj }},'
        ' but a hungry stare stopped you.'
    ])
    combine_else_replies = Reply([
        '{{ object | predobj }} showed no interest'
        ' in {{ item | predobj}}.'
    ])

    def __init__(self, *args, name=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.named = name
        self.state['rabbit'] = 'hungry'

        self.actions['touch'] = self.touch_replies
        self.actions['look'] = self.look
        self.actions['speak'] = self.speak_replies
        self.actions['combine'] = self.combine
        self.actions['apply'] = self.apply

    def name(self):
        return self.named

    def short_name(self):
        return 'rabbit'

    def proper_name(self):
        return True

    def look(self, data):
        if self.state['rabbit'] == 'hungry':
            raise self.look_hungry_replies.say(data)
        else:
            data['item'] = self.state['food']
            raise self.look_fed_replies.say(data)

    def combine(self, data):
        action = data['action']

        item = action.predicate
        if item is None:
            raise InvalidInteraction()

        if item.name() == 'carrot':
            self.apply(data)
        else:
            raise self.combine_else_replies.say(data)

    def apply(self, data):
        action = data['action']

        item = action.predicate
        if item is None:
            raise InvalidInteraction()

        if item.name() == 'carrot':
            if self.state['rabbit'] != 'fed':
                item.set_parent(self)
                self.state['food'] = item
                self.state['rabbit'] = 'fed'
                raise self.combine_carrot_replies.say(data)
            else:
                raise self.combine_carrot_fed_replies.say(data)
        else:
            raise self.combine_else_replies.say(data)

if __name__ == '__main__':

    nar = Narrator()

    r = Balkony(nar, 'room001')
    nar.inventory_add_object(Carrot(nar, 'carrot1', pred=Predicate('first')))
    nar.inventory_add_object(Carrot(nar, 'carrot2', pred=Predicate('second')))
    r.add_object(Rabbit(nar, 'bowser', name='bowser'))
    r.add_object(Rabbit(nar, 'cooper', name='cooper'))
    r.add_door(Door(nar, 'door003', pred=Predicate('back')))
    nar.enter(r)

    nar.interact('look')
    nar.interact('look at door')
    nar.interact('look at cooper')
    nar.interact('look at bowser')
    nar.interact('look inventory')
#    nar.interact('behold carrot')
#    nar.interact('look at carrot')

#
#    nar.interact('behold left door')
#    nar.interact('behold left door')
#    nar.interact('behold left door')
#    nar.interact('behold left door')
#
#    nar.interact('look at rabbit')
#    nar.interact('look at cooper')
#    nar.interact('look behind cooper')
#
    nar.interact('look at first carrot')
    nar.interact('look at second carrot')
#    nar.interact('look at cooper')
    nar.interact('give first carrot to cooper')
    nar.interact('give second carrot to cooper')
    nar.interact('give second carrot to bowser')
#    nar.interact('look cooper')
#    nar.interact('look behind cooper')
#    nar.interact('combine carrot and cooper')
#
#    nar.interact('foo')
#    nar.interact('look at car')
#
#    nar.interact('look at left door')
#    nar.interact('use left door')
#    nar.interact('use carrot with bowser')
#
#    nar.interact('look rabbit')
#    nar.interact('touch bowser')
#    nar.interact('look bowser')
#    nar.interact('look bowser')
#    nar.interact('speak bowser')
#
#    nar.interact('use carrot on rabbit')
#
#    nar.interact('speak left door')
#
#
#    nar.interact('behold door')
#    nar.interact('look behind left door')
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
