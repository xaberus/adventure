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
            'You {{ verb | past }} the {{ object | obj }}.',
        ])
        self.open_open_replies = Reply([
            'The {{ object | obj }} was already open;'
            ' any attempt to {{ verb | inf }} it any more was futile.'
        ])
        self.open_locked_replies = Reply([
            'The {{ object | obj }} was locked,'
            ' you could not {{ verb | inf }} it.',
            'You tried to {{ verb | inf }} the'
            ' {{ object | obj }}, but it still was locked.',
        ])
        self.actions['open'] = self.open

        # close
        self.close_open_replies = Reply([
            'You {{ verb | past }} the {{ object | obj }}.',
        ])
        self.close_closed_replies = Reply([
            'You could not {{ verb | inf }} the {{ object | obj }}'
            ' as was already closed.',
            'You decided not to {{ verb | inf }} the {{ object | obj }}'
            ' any further.',
        ])
        self.close_locked_replies = Reply([
            'Your attempts to {{ verb | inf }} the locked {{ object | obj }}'
            ' were not successfull.',
        ])
        self.actions['close'] = self.close

        # look
        self.look_open_replies = NarrativeReply('easteregg.doors1', [
            'The {{ object | obj }} was open.',
            'You see a perfectly normal open {{ object | obj }}.',
        ], [
            'A wise man once said: If you stare into the door...',
            'the door will stare into you.',
            'Or something like this...',
            'It is rude to stare!',
        ])
        self.look_closed_replies = NarrativeReply('easteregg.doors1', [
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
            self.open_closed_replies.say(self.nar, data)
            state = 'open'
        elif state == 'open':
            self.open_open_replies.say(self.nar, data)
        elif state == 'locked':
            self.open_locked_replies.say(self.nar, data)
        elif state == 'jammed':
            self.jammed_replies.say(self.nar, data)

    def close(self, data):
        state = self.state['door']
        if state == 'open':
            self.close_open_replies.say(self.nar, data)
            state = 'closed'
        elif state == 'closed':
            self.close_closed_replies.say(self.nar, data)
        elif state == 'locked':
            self.close_locked_replies.say(self.nar, data)
        elif state == 'jammed':
            self.jammed_replies.say(self.nar, data)

    def look(self, data):
        state = self.state['door']
        if state == 'open':
            self.look_open_replies.narrate(self.nar, data)
        elif state in ('closed', 'locked', 'jammed'):
            self.look_closed_replies.narrate(self.nar, data)


class MetalDoor(Door):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.look_closed_replies.set_variants([
            'You {{ verb | past }}'
            ' the {{ object | obj }}.'
            ' It was a heavy {{ object | obj }} with strange markings'
            ' that strangely remindend you of something.'
        ])

        self.touch_replies = Reply([
            'The {{ object | obj }} was cold to the touch.'
        ])
        self.actions['touch'] = self.touch

    def name(self):
        return 'metal door'

    def short_name(self):
        return 'door'

    def touch(self, data):
        self.touch_replies.narrate(self.nar, data)
