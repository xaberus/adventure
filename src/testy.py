# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 23:41:51 2017

@author: xa
"""

import os
import game


class Item(game.object.Object):
    def __init__(self, nar, uid, data):
        keys = data.keys()

        for key in keys:
            if key.startswith('reply@'):
                data.pop(key)

        super().__init__(nar, uid, data)


class ActionReplyMap:
    def __init__(self, state, activation_map):
        self._state = state
        self._actions = {}
        self._activation_map = activation_map

    def _parse_spec(self, spec):
        head, tail = spec.split('@')
        try:
            action, tail = tail.split('/')
            try:
                tags = tail.split(',')
            except ValueError:
                tags = [tail]
        except ValueError:
            action = tail
            tags = []
        return head, action, tuple(tags)

    def add_action_reply(self, spec, reply_data):
        head, action, tags = self._parse_spec(spec)
        print(action, tags)
        if head == 'reply':
            reply = game.reply.Reply(reply_data)
        else:
            raise ValueError('unknown reply type `{}`'.format(head))

        if action not in self._actions:
            self._actions[action] = []

        self._actions[action].append((tags, reply))

    def handle_action(self, action, data):
        #print(action, data)
        if action not in self._actions:
            raise game.object.InvalidInteraction()

        out = []
        for tags, reply in self._actions[action]:
            match = True
            for tag in tags:
                if tag[0] == '!':
                    tag = tag[1:]
                    match = match and not self._state[tag]
                else:
                    match = match and self._state[tag]
            if match:
                out.append(reply.text(data))
        raise game.reply.NarratorAnswer(' '.join(out))


class ItemReceiver(game.object.Object):
    def __init__(self, nar, uid, data):
        keys = data.keys()

        actions = []
        activation_map = None

        for key in keys:
            if key.startswith('reply@'):
                actions.append((key, data.pop(key)))
            elif key == 'activation_map':
                activation_map = data.pop(key)

        super().__init__(nar, uid, data)

        self._arm = ActionReplyMap(self._state, activation_map)

        for spec, reply_data in actions:
            self._arm.add_action_reply(spec, reply_data)

    def interact(self, action):
        data = {
            'action': action,
            'object': self,
            'item': action.predicate,
        }

        base = action.base
        try:
            self._arm.handle_action(base, data)
        except game.object.InvalidInteraction:
            raise self.unknown_replies.complain(data)


if __name__ == '__main__':
    game.registry.register_object_classes(game.object.Object)

    nar = game.narrator.Narrator()
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    game.state.load(nar, data_path, 'test_0.yaml')

    commands = """
        look inventory
        look
        look robot
        look rabbit
        look long carrot
        touch first rabbit
        look second rabbit
        look second rabbit
        pet second rabbit
    """

    for cmd in commands.split('\n'):
        nar.interact(cmd.strip())

    print(nar.state().current_room().dump())
    print(nar.state().current_room().get_by_uid('bowser').name().variants())
