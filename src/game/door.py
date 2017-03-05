# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 23:43:09 2017

@author: xa
"""

import game.dictionary
from game.object import Object
from game.reply import Reply, NarrativeReply
from game.name import ObjectName
from game.predicate import Predicate


class Door(Object):
    def __init__(self, nar, uid, data):
        if 'name' not in data:
            data['name'] = ObjectName(game.dictionary.nouns['door'])
        if 'location' not in data:
            data['location'] = None
        state = data.pop('state', None)
        super().__init__(nar, uid, data)

        if state is None:
            state = 'closed'
        self._state['state'] = state

        # open
        self.open_closed_replies = Reply([
            'You {{ action | past }} {{ object | namdefl }}.',
        ])
        self.open_open_replies = Reply([
            '{{ object | namdefl | cap }} was already open;'
            ' any attempt to {{ action | inf }} it any more was futile.'
        ])
        self.open_locked_replies = Reply([
            '{{ object | namdefl| cap }} was locked,'
            ' you could not {{ action | inf }} it.',
            'You tried to {{ action | inf }}'
            ' {{ object | namdefl }}, but it still was locked.',
        ])
        self.actions['open'] = self.open

        # close
        self.close_open_replies = Reply([
            'You {{ action | past }} {{ object | namdefl }}.',
        ])
        self.close_closed_replies = Reply([
            'You could not {{ action | inf }} {{ object | namdefl }}'
            ' as was already closed.',
            'You decided not to {{ action | inf }} {{ object | namdefl }}'
            ' any further.',
        ])
        self.close_locked_replies = Reply([
            'Your attempts to {{ action | inf }} {{ object | namdefl }}'
            ' were not successfull, as it was locked.',
        ])
        self.actions['close'] = self.close

        nar = self.nar
        # look
        self.look_open_replies = NarrativeReply(nar, 'easteregg.doors1', [
            'The {{ object | namdefl }} was open.',
            'You saw a perfectly normal open {{ object | namsimp }}.',
        ], [
            'A wise man once said: If you stare into the door...',
            'the door will stare into you.',
            'Or something like this...',
            'It is rude to stare!',
        ])
        self.look_closed_replies = NarrativeReply(nar, 'easteregg.doors1', [
            'It was just a closed {{ object | namsimp }}.'
            ' Nothing particular was special about it.'
        ], [
            'You wondered what hid behind {{ object | namdefl }}.',
            'It was bigger than a window and smaller than a gate,'
            ' so, by your definition, it was a door.',
        ])
        self.actions['look'] = self.look

        # jammed
        self.jammed_replies = Reply([
            '{{ object | namdefl | cap }} was jammed shut.'
            ' You could not do anything about it.'
        ])

    def open(self, data):
        state = self._state['door']
        if state == 'closed':
            self.state['door'] = 'open'
            raise self.open_closed_replies.say(data)
        elif state == 'open':
            raise self.open_open_replies.say(data)
        elif state == 'locked':
            raise self.open_locked_replies.say(data)
        elif state == 'jammed':
            raise self.jammed_replies.say(data)

    def close(self, data):
        state = self._state['door']
        if state == 'open':
            self.state['door'] = 'closed'
            raise self.close_open_replies.say(data)
        elif state == 'closed':
            raise self.close_closed_replies.say(data)
        elif state == 'locked':
            raise self.close_locked_replies.say(data)
        elif state == 'jammed':
            raise self.jammed_replies.say(data)

    def look(self, data):
        state = self._state['door']
        if state == 'open':
            raise self.look_open_replies.narrate(data)
        elif state in ('closed', 'locked', 'jammed'):
            raise self.look_closed_replies.narrate(data)


class MetalDoor(Door):
    def __init__(self, *args, **kwargs):
        if 'name' not in kwargs:
            noun = game.dictionary.nouns['door']
            pred = Predicate([
                game.dictionary.adjectives['metal']
            ])
            kwargs['name'] = ObjectName(noun, pred=pred)
        if 'location' not in kwargs:
            kwargs['location'] = None
        super().__init__(nar, uid, **kwargs)

        self.look_closed_replies.set_variants([
            'You {{ action | past }}'
            ' {{ object | namdefl }}.'
            ' It was a heavy {{ object | kind | namsimp }} with'
            ' strange markings that strangely remindend you of something.'
        ])

        self.touch_replies = Reply([
            '{{ object | namdefl | cap }} was cold to the touch.'
        ])
        self.actions['touch'] = self.touch_replies


