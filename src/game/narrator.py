# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:22:40 2017

@author: xa
"""

import re
import collections
import game.verb
from game.action import InvalidPreposition, Action
from game.environment import env, debug
from game.object import InvalidInteraction, Container
from game.reply import Reply, RandomReply
from game.reply import NarratorAnswer, NarratorNarration, NarratorComplaint
from game.room import Room


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


class Inventory(Room):

    inventory_empty_replies = Reply([
        '{{ object | predobj }} was empty.'
    ])

    inventory_replies = Reply([
        'You took a look at {{ object | obj }}:'
        '\n\n'
        '{% for item in objects %}'
        '  {{ item | predobj }}'
        '{% if not loop.last %}\n{% endif %}'
        '{% endfor %}'
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.actions['look'] = self.look

    def name(self):
        return 'your inventory'

    def short_name(self):
        return 'inventory'

    def __repr__(self):
        out = []
        for item in self.objects:
            out.append(str(item))
        return '<inventory [{}]>'.format(', '.join(out))

    def look(self, data):
        if len(self.objects) == 0:
            raise self.inventory_empty_replies.say(data)

        data['objects'] = self.objects.values()

        raise self.inventory_replies.say(data)


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
            ' {{ room | point }} {{ room | predobj }}.'
            ' Did you mean{% for target in targets[:-1] %}'
            ' {{ target| predobj }}{% if not loop.last %},{% endif %}'
            '{%endfor%}'
            '{% for target in targets[-1:] %}'
            ' or'
            ' {{ target| predobj }}'
            '{%endfor%}.'
        ])

        self.no_target_reply = Reply([
            'Your call for {{ action| ing }} was fruitless,'
            ' as it was missing a target.'
        ])

        self.target_not_found_reply = RandomReply([
            'You tried to {{ action| inf }} the'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}...'
            ' As there was nothing that looked like '
            '{% for token in tokens %} {{ token | upper }}'
            '{% endfor %} {{ room | point }} {{ room | predobj }},'
            ' you cried in desperation.',

            'In your head you thought about'
            ' {{ action | ing }} the'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}...'
            ' The problem was that such a thing was nowhere to be found.',

            'You searched {{ room | predobj }}, but you could not find'
            '{% for token in tokens %} {{ token | upper }}'
            '{% endfor %}.',

            'You neither possessed not saw anything that reminded you of'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}.',

            'Unfortunately, the fate did not endow you with'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}.',
        ])

        self.not_parsed_reply = RandomReply([
            'The echo friendly repeated your gobbledygook.',
            'Your words had no meaning in that context.'
        ])

        self.actions['utilize'] = self.parse_complex_action
        self.actions['play'] = self.parse_complex_action
        self.actions['ramble'] = self.parse_complex_action

    def enter(self, room):
        self.room = room

    def find_object(self, action, tokens):
        debug('[find object]', action, tokens)
        try:
            idn = tuple(tokens)
            try:
                target = self.inventory.find(idn)
                room = self.inventory
            except KeyError:
                target = self.room.find(idn)
                room = self.room
            if len(target) > 1:
                raise TargetNotUnique(room, action, tokens, target)
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
        try:
            action = Action(verb)
        except KeyError:
            raise ParseFailed()

        return self.parse_action(action, tokens[1:])

    def parse_action(self, action, tokens):
        base = action.base
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
            action.set_target(self.room)

        return action

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
            return self.parse_simple_action(action, tokens)
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
                    'room': self.room,
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

    def narrate(self, msg):
        if len(msg) > 0:
            print('{narrating} ' + msg)

    def complain(self, msg):
        if len(msg) > 0:
            print('{complaining} ' + msg)

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
