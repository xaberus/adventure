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

from game.name import ObjectName
from game.action import InvalidPreposition, Action
from game.environment import env
from game.util import debug
from game.object import InvalidInteraction
from game.reply import Reply, RandomReply
from game.reply import NarratorAnswer, NarratorNarration, NarratorComplaint
from game.room import Room
from game.location import Location


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


class Inventory(Room):

    inventory_empty_replies = Reply([
        '{{ object | namdefl }} was empty.'
    ])

    inventory_replies = Reply([
        'You took a look in {{ object | namdefl }}:'
        '\n\n'
        '{% for item in objects %}'
        '  {{ item | namdefl }}'
        '{% if not loop.last %}\n{% endif %}'
        '{% endfor %}'
    ])

    def __init__(self, nar, uid, **kwargs):
        name = ObjectName(game.dictionary.nouns['inventory'])
        kwargs['name'] = name
        kwargs['location'] = Location(name=name, point_to="in your inventory")
        super().__init__(nar, uid, **kwargs)

        self.actions['look'] = self.look

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

        self.rooms = {}

        self.env = env
        self.room = None
        self.level = None

        self.not_unique_reply = Reply([
            'There were more than one'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}'
            ' {{ room | location | namdefl }} {{ room | namdefl }}.'
            ' Did you mean{% for target in targets[:-1] %}'
            ' {{ target| namdefl }}{% if not loop.last %},{% endif %}'
            '{%endfor%}'
            '{% for target in targets[-1:] %}'
            ' or'
            ' {{ target| namdefl }}'
            '{%endfor%}.'
        ])

        self.no_target_reply = Reply([
            'Your call for {{ action| ing }} was fruitless,'
            ' as it was missing a target.'
        ])

        self.target_not_found_reply = RandomReply([
            'You tried to {{ action.verb | inf }} the'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}...'
            ' As there was nothing that looked like '
            '{% for token in tokens %} {{ token | upper }}'
            '{% endfor %} {{ room | location | namdefl }}'
            ' {{ room | namdefl }},'
            ' you cried in desperation.',

            'In your head you thought about'
            ' {{ action | ing }}'
            '{% if action | prep %}{{ action | prep }}{% endif %}'
            ' the'
            '{% for token in tokens %}'
            ' {{ token | upper }}'
            '{% endfor %}...'
            ' The problem was that such a thing was nowhere to be found.',

            'You searched {{ room | namdefl }}, but you could not find'
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

        self.actions['use'] = self.parse_complex_action
        self.actions['give'] = self.parse_complex_action

    def enter(self, room):
        debug('[enter]', room)
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
            action.set_target(self.room)

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

    def require_uid_state(self, uid, state):
        if state is None:
            state = {}

        m = re.match('[a-z0-9_]+', uid)
        if m is None:
            raise KeyError('malformed uid {}'.format(uid))

        if uid not in self.state:
            self.state[uid] = state

        return self.state[uid]

    def inventory_add_object(self, obj):
        self.inventory.add_object(obj)

    def load(self, file_name):
        data_dir = os.path.dirname(__file__)
        level_path = os.path.join(data_dir,
                                  '..',
                                  'data',
                                  file_name)

        data = ordered_load(open(level_path, 'r'))

        rooms_data = data['rooms']
        for room_uid, room_data in rooms_data.items():
            room = game.object.create(self, room_uid, room_data)
            self.rooms[room_uid] = room

        inventory_data = data['inventory']
        inventory = game.location.create({
            'name': {
                'noun': 'inventory',
            },
            'point_to': 'in your inventory',
        })
        for item_uid, item_data in inventory_data.items():
            item_data['location'] = inventory
            item = game.object.create(self, item_uid, item_data)
            self.inventory_add_object(item)

        start_room = data['start_room']

        self.enter(self.rooms[start_room])
