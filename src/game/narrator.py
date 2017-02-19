# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:22:40 2017

@author: xa
"""

import re
import collections
import game.verb
import game.action
from game.environment import env
from game.object import InvalidInteraction, Container
from game.reply import Reply, RandomReply
from game.room import Room


class ParseFailed(Exception):
    pass

class TargetNotFound(Exception):
    def __init__(self, action, tokens):
        self.action = action
        self.tokens = tokens


class TargetNotUnique(Exception):
    def __init__(self, action, tokens, target):
        self.action = action
        self.tokens = tokens
        self.target = target


class Inventory(Room):
    pass


class Narrator:
    def __init__(self):
        self.state = {}
        self.state['@narratives'] = {}
        self.narratives = self.state['@narratives']
        self.inventory = Inventory(self, 'inventory')
        self.actions = {}

        self.env = env
        self.room = None

        self.not_unique_reply = Reply([
            'There were more than one'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}'
            ' in the {{ room | predobj }}.'
            ' Did you mean{% for target in targets[:-1] %}'
            ' {{ target| predobj }}{% if not loop.last %},{% endif %}'
            '{%endfor%}'
            '{% for target in targets[-1:] %}'
            ' or'
            ' {{ target| predobj }}'
            '{%endfor%}.'
        ])

        self.no_target_reply = Reply([
            'Your call for {{ verb| ing }} was fruitless,'
            ' as it was missing a target.'
        ])

        self.target_not_found_reply = RandomReply([
            'You tried to {{ verb| inf }} the'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}'
            '. It was not there. You cried in desperation.',
            'In your head'
            ' {{ verb | ing }} the'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}'
            ' sounded particularly nice, but as soon as you tried to'
            ' say it aloud, it suddenly lost any sense.'
        ])
    
        self.not_parsed_reply = RandomReply([
            'The echo friendly repeated your gobbledygook.',
            'Your words had no meaning in that context.'
        ])
    
        self.actions['use'] = self.parse_use_action

    def enter(self, room):
        self.room = room
        
    def find_object(self, action, tokens):
        try:
            idn = tuple(tokens)
            try:
                target = self.inventory.find(idn)
            except KeyError:
                target = self.room.find(idn)
            if len(target) > 1:
                raise TargetNotUnique(action, tokens, target)
            return target[0]
        except KeyError:
            raise TargetNotFound(action, tokens)


    def parse(self, l):
        l = l.lower()
        tokens = l.split()

        if self.room is None:
            raise KeyError('no room')
            
        if len(tokens) >= 1:
            try:
                verb = game.verb.verbs[tokens[0]]
            except KeyError:
                raise ParseFailed()
            
        # verb must be defined below here
        action = game.action.actions[verb.base]
        base = action.base
        
        if base not in self.actions:
            return self.parse_simple_action(action, tokens[1:])
        else:
            return self.actions[base](action, tokens[1:])
        
        
    def parse_simple_action(self, action, tokens):
        if len(tokens) >= 1:
            prep = action.verb.preposition()
            if prep is not None and tokens[0] == prep:
                tokens = tokens[1:]
            
        if len(tokens) >= 1:
            target = self.find_object(action, tokens)
        else:
            return 'simple', action, self.room

        return 'simple', action, target
    
    def parse_use_action(self, action, tokens):
        preps = action.verb.extra_prepositions()
        object_a = None
        object_b = None
        
        split = None
        for prep in preps:
            if prep in tokens:
                split = prep
                break
            
        if split is None:
            found = False
            try:
                for i in range(1, len(tokens)):
                    tokens_a = tokens[0:i]
                    tokens_b = tokens[i:]
                    
                    object_a = self.find_object(action, tokens_a)
                    object_b = self.find_object(action, tokens_b)
                    found = True
                    break
            except Exception as e:
                pass
            if not found:
                return self.parse_simple_action(action, tokens)
        else:          
            i = tokens.index(prep)
            tokens_a = tokens[0:i]
            tokens_b = tokens[i + 1:]
        
            object_a = self.find_object(action, tokens_a)
            object_b = self.find_object(action, tokens_b)
        
        return 'janus', action, object_a, object_b
        
    def interact(self, l):
        print('> {}'.format(l))
        try:
            t = self.parse(l)
            if t[0] == 'simple':
                _, action, target = t
                target.interact(action)
            elif t[0] == 'janus':
                _, action, object_a, object_b = t
                try: 
                    object_a.interact(action, object_b)
                except InvalidInteraction:
                    object_b.interact(action, object_a)
            else:
                raise ParseFailed()
        except TargetNotFound as e:
            self.target_not_found_reply.complain(self, {
                'action': e.action,
                'verb': e.action.verb,
                'tokens': e.tokens,
            })
        except TargetNotUnique as e:
            self.not_unique_reply.complain(self, {
                'action': e.action,
                'verb': e.action.verb,
                'tokens': e.tokens,
                'targets': e.target,
                'room': self.room,
            })
        except ParseFailed as e:
            self.not_parsed_reply.complain(self, {
            })
        except InvalidInteraction as e:
            pass
                
    def say(self, msg):
        if len(msg) > 0:
            print(msg)

    def narrate(self, msg):
        if len(msg) > 0:
            print(msg)

    def complain(self, msg):
        if len(msg) > 0:
            print(msg)

    def get_narrative(self, narrative_id):
        if narrative_id not in self.narratives:
            self.narratives[narrative_id] = {}
        return self.narratives[narrative_id]

    def require_uid_state(self, uid):
        m = re.match('[a-z0-9_]+', uid)
        if m is None:
            raise KeyError('malformed uid')

        if uid not in self.state:
            self.state[uid] = {}

        return self.state[uid]

    def inventory_add_object(self, obj):
        self.inventory.add_object(obj)
