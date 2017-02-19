# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 23:43:09 2017

@author: xa
"""

from game.object import Object
from game.reply import Reply, NarrativeReply


class Door(Object):
    def __init__(self, *args, state=None, **kwargs):
        super().__init__(*args, **kwargs)

        if state is None:
            state = 'closed'
        self.state['door'] = state

        # open
        self.open_closed_replies = Reply([
            'You {{ action | past }} the {{ object | obj }}.',
        ])
        self.open_open_replies = Reply([
            'The {{ object | obj }} was already open;'
            ' any attempt to {{ action | inf }} it any more was futile.'
        ])
        self.open_locked_replies = Reply([
            'The {{ object | obj }} was locked,'
            ' you could not {{ action | inf }} it.',
            'You tried to {{ action | inf }} the'
            ' {{ object | obj }}, but it still was locked.',
        ])
        self.actions['open'] = self.open

        # close
        self.close_open_replies = Reply([
            'You {{ action | past }} the {{ object | obj }}.',
        ])
        self.close_closed_replies = Reply([
            'You could not {{ action | inf }} the {{ object | obj }}'
            ' as was already closed.',
            'You decided not to {{ action | inf }} the {{ object | obj }}'
            ' any further.',
        ])
        self.close_locked_replies = Reply([
            'Your attempts to {{ action | inf }} the locked {{ object | obj }}'
            ' were not successfull.',
        ])
        self.actions['close'] = self.close

        nar = self.nar
        # look
        self.look_open_replies = NarrativeReply(nar, 'easteregg.doors1', [
            'The {{ object | obj }} was open.',
            'You see a perfectly normal open {{ object | obj }}.',
        ], [
            'A wise man once said: If you stare into the door...',
            'the door will stare into you.',
            'Or something like this...',
            'It is rude to stare!',
        ])
        self.look_closed_replies = NarrativeReply(nar, 'easteregg.doors1', [
            'It was just a closed {{ object | obj }}.'
            ' Nothing particular was special about it.'
        ], [
            'You wondered what hid behind the {{ object | obj }}.',
            'It was bigger than a window and smaller than a gate,'
            ' so, by your definition, it was a door.',
        ])
        self.actions['look'] = self.look

        # jammed
        self.jammed_replies = Reply([
            'The {{ object | obj }} was jammed shut.'
            ' You could not do anything about it.'
        ])

    def name(self):
        return 'door'

    def descibe(self):
        return 'Just a simple door.'

    def open(self, data):
        state = self.state['door']
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
        state = self.state['door']
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
        state = self.state['door']
        if state == 'open':
            raise self.look_open_replies.narrate(data)
        elif state in ('closed', 'locked', 'jammed'):
            raise self.look_closed_replies.narrate(data)


class MetalDoor(Door):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.look_closed_replies.set_variants([
            'You {{ action | past }}'
            ' the {{ object | obj }}.'
            ' It was a heavy {{ object | obj }} with strange markings'
            ' that strangely remindend you of something.'
        ])

        self.touch_replies = Reply([
            'The {{ object | obj }} was cold to the touch.'
        ])
        self.actions['touch'] = self.touch_replies

    def name(self):
        return 'metal door'

    def short_name(self):
        return 'door'
