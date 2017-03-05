# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:22:40 2017

@author: xa
"""

import os
import re
import yaml
import collections
import game.verb
import game.dictionary
import game.registry

from game.action import InvalidPreposition, Action
from game.environment import env
from game.util import debug
from game.object import InvalidInteraction
from game.reply import Reply, RandomReply
from game.reply import NarratorAnswer, NarratorNarration, NarratorComplaint
from game.inventory import Inventory


def ordered_load(stream):
    class OrderedLoader(yaml.Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return collections.OrderedDict(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


class ParseFailed(Exception):
    pass


class TargetNotFound(Exception):
    def __init__(self, action, tokens):
        self.action = action
        self.tokens = tokens


class TargetNotUnique(Exception):
    def __init__(self, room, action, tokens, target):
        self.room = room
        self.action = action
        self.tokens = tokens
        self.target = target


class Narrator:
    def __init__(self):
        self.actions = {}

        self.rooms = {}

        self.env = env

        self.not_unique_reply = Reply([
            'There were more than one'
            '{% for token in tokens %}'
            ' {{ token | brk }}'
            '{% endfor %}'
            ' {{ room | location | brk }}.'
            ' Did you mean{% for target in targets[:-1] %}'
            ' {{ target| namdefl | brk }}'
            '{% if not loop.last %},{% endif %}'
            '{%endfor%}'
            '{% for target in targets[-1:] %}'
            ' or'
            ' {{ target| namdefl | brk }}'
            '{%endfor%}.'
        ])

        self.no_target_reply = Reply([
            'Your call for {{ action| ing | brk }} was fruitless,'
            ' as it was missing a target.'
        ])

        self.target_not_found_reply = RandomReply([
            'You tried to {{ action.verb | inf | brk }}'
            '{% for token in tokens %}'
            ' {{ token | brk }}'
            '{% endfor %}...'
            ' As there was nothing that looked like'
            '{% for token in tokens %} {{ token | brk }}'
            '{% endfor %} {{ room | location | brk }},'
            ' you cried in desperation.',

            'In your head you thought about'
            ' {{ action.verb | ing | brk }}'
            ' the'
            '{% for token in tokens %}'
            ' {{ token | brk }}'
            '{% endfor %}...'
            ' The problem was that such a thing was nowhere to be found.',

            'You searched {{ room | namdefl | brk }}, but you could not find'
            '{% for token in tokens %} {{ token | brk | brk }}'
            '{% endfor %}.',

            'You neither possessed not saw anything that reminded you of'
            '{% for token in tokens %}'
            ' {{ token | brk }}'
            '{% endfor %}.',

            'Unfortunately, the fate did not endow you with'
            '{% for token in tokens %}'
            ' {{ token | brk }}'
            '{% endfor %}.',
        ])

        self.not_parsed_reply = RandomReply([
            'The echo friendly repeated your gobbledygook.',
            'Your words had no meaning in that context.'
        ])

        self.actions['use'] = self.parse_complex_action
        self.actions['give'] = self.parse_complex_action

    def set_state(self, state):
        self._state = state

    def state(self):
        return self._state

    def enter(self, room):
        self._state.enter_room(room)

    def find_object(self, action, tokens):
        debug('[find object]', action, tokens)
        try:
            idn = tuple(tokens)
            try:
                target = self._state.inventory_find(idn)
                room = self._state.inventory()
            except KeyError:
                target = self._state.current_room().find(idn)
                room = self._state.current_room()
            if len(target) > 1:
                raise TargetNotUnique(room, action, tokens, target)
            return target[0]
        except KeyError:
            raise TargetNotFound(action, tokens)

    def parse(self, l):
        l = l.lower()
        tokens = l.split()

        if self._state.current_room() is None:
            raise KeyError('no room')

        if len(tokens) >= 1:
            try:
                verb = game.verb.verbs[tokens[0]]
            except KeyError:
                raise ParseFailed()

        # verb must be defined below here
        try:
            action = Action(verb)
        except KeyError:
            raise ParseFailed()

        return self.parse_action(action, tokens[1:])

    def parse_action(self, action, tokens):
        base = action.verb.base
        if base not in self.actions:
            return self.parse_simple_action(action, tokens)
        else:
            return self.actions[base](action, tokens)

    def parse_simple_action(self, action, tokens):
        if len(tokens) >= 1:
            preps = action.verb.local_prepositions()
            if tokens[0] in preps:
                action.set_local_preposition(tokens[0])
                tokens = tokens[1:]

        if len(tokens) >= 1:
            action.set_target(self.find_object(action, tokens))
        else:
            action.set_target(self._state.current_room())

        return action

    def default_complex_preposition(self, action):
        vbase =action.verb.base
        if vbase == 'give':
            return True, 'to'

    def parse_complex_action(self, action, tokens):
        preps = action.verb.far_prepositions()
        object_a = None
        object_b = None

        split = None
        for prep in preps:
            if prep in tokens:
                split = prep
                break

        if split is None:
            found = False
            for i in range(1, len(tokens) - 1):
                tokens_a = tokens[0:i]
                tokens_b = tokens[i:]

                try:
                    object_a = self.find_object(action, tokens_a)
                    object_b = self.find_object(action, tokens_b)
                except:
                    continue
                found = True
                break

            if not found:
                return self.parse_simple_action(action, tokens)

            reverse, prep = self.default_complex_preposition(action)
            action.set_far_preposition(prep)
            if reverse:
                object_a, object_b = object_b, object_a
            debug('[complex parse for]', object_a, object_b)

        else:
            i = tokens.index(prep)
            action.set_far_preposition(tokens[i])

            tokens_a = tokens[0:i]
            tokens_b = tokens[i + 1:]

            object_a = self.find_object(action, tokens_a)
            object_b = self.find_object(action, tokens_b)

        # WARNING: reversed order
        action.set_target(object_b)
        action.set_predicate(object_a)

        return action

    def interact(self, l):
        l = l.strip()
        if l == '':
            return
        if l.startswith('#'):
            return

        print('> {}'.format(l))
        try:
            try:
                action = self.parse(l)
                debug('[parsed action]', action)
                self.execute_action(action)
            except TargetNotFound as e:
                raise self.target_not_found_reply.complain({
                    'action': e.action,
                    'tokens': e.tokens,
                    'room': self._state.current_room(),
                })
            except TargetNotUnique as e:
                raise self.not_unique_reply.complain({
                    'action': e.action,
                    'tokens': e.tokens,
                    'targets': e.target,
                    'room': e.room,
                })
            except ParseFailed as e:
                raise self.not_parsed_reply.complain({
                })
            except InvalidInteraction as e:
                raise self.not_parsed_reply.complain({
                })
            except InvalidPreposition as e:
                raise self.not_parsed_reply.complain({
                })
        except NarratorAnswer as e:
            self.say(e.message)
        except NarratorNarration as e:
            self.narrate(e.message)
        except NarratorComplaint as e:
            self.complain(e.message)

    def execute_action(self, action):
        try:
            action.target.interact(action)
        except NarratorComplaint as e:
            try:
                if action.base in ['combine']:
                    new_action = action.swap_taget_and_predicate()
                    debug('[parsed action (swapped)]', new_action)
                    new_action.target.interact(new_action)
                else:
                    raise e
            except NarratorComplaint:
                raise e

    def say(self, msg):
        if len(msg) > 0:
            print(msg)
            print()

    def narrate(self, msg):
        if len(msg) > 0:
            print('{narrating} ' + msg)
            print()

    def complain(self, msg):
        if len(msg) > 0:
            print('{complaining} ' + msg)
            print()


