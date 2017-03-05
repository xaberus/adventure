# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:27:10 2017

@author: xa
"""

import game.dictionary
from game.predicate import Predicate
from game.room import Room
from game.doors import Door, MetalDoor
from game.object import InvalidInteraction, Object
from game.reply import Reply
from game.narrator import Narrator
from game.name import ObjectName
from game.location import Location

import game.registry

class Balkony(Room):
    description = (
        'Your {{ object | namsimp }} looked like always.'
        ' A gentle rustle was the evidence of your two favorite rabbits:'
        ' Cooper and Bowser.'
    )

    def __init__(self, nar, uid, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = ObjectName(game.dictionary.nouns['balkony'])
        kwargs['location'] = Location('on {{ room | namdefl }}')

        super().__init__(nar, uid, **kwargs)


class Carrot(Object):
    def __init__(self, nar, uid, **kwargs):
        pred = kwargs.pop('pred', None)
        if 'name' not in kwargs:
            noun = game.dictionary.nouns['carrot']
            kwargs['name'] = ObjectName(noun, pred=pred)
        super().__init__(nar, uid, **kwargs)

        self.look_replies = Reply([
            '{{ object | namdefn }} was fresh and looked tasty.'
            ' At least if you were a hare or a rabbit.'
            ' For no aparent reason you knew that'
            ' this was {{ object | namdefl }}.'
        ])
        self.actions['look'] = self.look_replies


class Rabbit(Object):
    touch_replies = Reply([
        '{{ object | namdefl }} was warm and fluffy to the'
        ' {{ action | inf }}.'
    ])

    look_hungry_replies = Reply([
        'You mixed somehing up. {{ object | namdefl }} was looking at you.'
        ' You.'
        ' It wanted to be fed.',
        '{{ object | namdefl }}, one of your favourite rabbits'
        ' was looking at you.'
    ])
    look_fed_replies = Reply([
        '{{ object | namdefl }} was firmly holding {{ item | namdefn }}'
        ' in its tiny paws. It looked happy and for a moment you'
        ' imagened to see a glimpse of gratitude in its eyes.',
        '{{ object | namdefl }} was fed and happy. Your attention was not '
        'needed anymore.'
    ])

    speak_replies = Reply([
        'You {{ action | past }} {{ object | namdefl }}. You heared silence.'
        ' What did you expect?'
    ])

    combine_carrot_replies = Reply([
        '{{ object | namdefl }} snatched {{ item | namdefl }} from'
        ' your hand.',
        'You gave {{ item | namdefl }} to {{ object | namdefl }}.'
        ' Silently you remarked something about order not having'
        ' a particular meaning.'
    ])
    combine_carrot_fed_replies = Reply([
        'You almost gave the {{ item | namdefl }} to {{ object | namdefl }},'
        ' but a hungry stare stopped you.'
    ])
    combine_else_replies = Reply([
        '{{ object | kind | namdefl }} showed no interest'
        ' in {{ item | namdefl }}.'
    ])

    def __init__(self, nar, uid, **kwargs):
        super().__init__(nar, uid, **kwargs)

        self.state['rabbit'] = 'hungry'

        self.actions['touch'] = self.touch_replies
        self.actions['look'] = self.look
        self.actions['speak'] = self.speak_replies
        self.actions['combine'] = self.combine
        self.actions['apply'] = self.apply

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

if __name__ == 'not __main__':

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
    nar.interact('give bowser second carrot')
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

if __name__ == '__main__':
    game.registry.register_object_classes(Object)

#    import game.dictionary as gd
#    from game.word import Compound
#    from game.predicate import Predicate
#    from game.location import Location

    nar = Narrator()

    nar.load('level_0.yaml')
    nar.interact('look')
    nar.interact('look inventory')

#    r = Balkony(nar, 'balkony')
#    c = Carrot(nar, 'carrot1', pred=Predicate([
#        gd.adjectives['counting']['first']
#    ]), location=Location('on the floor'))
#    r.add_door(Door(nar, 'balkony_door', location=Location('in the back')))
#
#    nar.inventory_add_object(c)
#    nar.enter(r)
#
#    nar.interact('look')

#    nar.inventory_add_object(Carrot(nar, 'carrot1', pred=Predicate('first')))
#    nar.inventory_add_object(Carrot(nar, 'carrot2', pred=Predicate('second')))
#    r.add_object(Rabbit(nar, 'bowser', name='bowser'))
#    r.add_object(Rabbit(nar, 'cooper', name='cooper'))
#    r.add_door(Door(nar, 'door003', pred=Predicate('back')))
#    nar.enter(r)
