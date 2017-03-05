# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 23:41:51 2017

@author: xa
"""

import os
import game
from pyparsing import infixNotation, opAssoc, Word, alphas


class Item(game.object.Object):
    def __init__(self, nar, uid, data):
        keys = data.keys()

        for key in keys:
            if key.startswith('reply@'):
                data.pop(key)

        super().__init__(nar, uid, data)


class ActionReplyMap:
    class BoolOperand(object):
        def __init__(self, t):
            self.label = t[0]

        def __str__(self):
            return self.label
        __repr__ = __str__

        def eval(self, ctx):
            if self.label in ['True', 'true']:
                return True
            elif self.label in ['False', 'false']:
                return False
            return ctx[self.label]

    class BoolBinOp(object):
        def __init__(self, t):
            self.args = t[0][0::2]

        def __str__(self):
            sep = " %s " % self.reprsymbol
            return "(" + sep.join(map(str, self.args)) + ")"
        __repr__ = __str__

        def eval(self, ctx):
            return self.evalop(a.eval(ctx) for a in self.args)

    class BoolAnd(BoolBinOp):
        reprsymbol = '&'
        evalop = all

    class BoolOr(BoolBinOp):
        reprsymbol = '|'
        evalop = any

    class BoolNot(object):
        def __init__(self, t):
            self.arg = t[0][1]

        def __str__(self):
            return "!" + str(self.arg)
        __repr__ = __str__

        def eval(self, ctx):
            return not self.arg.eval(ctx)

    boolOperand = Word(alphas)
    boolOperand.setParseAction(BoolOperand)

    boolExpr = infixNotation(boolOperand, [
        ("!", 1, opAssoc.RIGHT, BoolNot),
        ("&", 2, opAssoc.LEFT,  BoolAnd),
        ("|",  2, opAssoc.LEFT,  BoolOr),
    ])

    def __init__(self, state, activation_map):
        self._state = state
        self._actions = {}
        self._activation_map = activation_map

    def _parse_spec(self, spec):
        head, tail = spec.split('@')
        try:
            action, tail = tail.split('/')
            expr = self.boolExpr.parseString(tail)[0]
        except ValueError:
            action = tail
            expr = self.boolExpr.parseString('True')[0]
        return head, action, expr

    def add_action_reply(self, spec, reply_data):
        head, action, expr = self._parse_spec(spec)
        # print(action, expr)
        if head == 'reply':
            reply = game.reply.Reply(reply_data)
        else:
            raise ValueError('unknown reply type `{}`'.format(head))

        if action not in self._actions:
            self._actions[action] = []

        self._actions[action].append((expr, reply))

    def handle_action(self, action, data):
        if action not in self._actions:
            raise game.object.InvalidInteraction()

        out = []
        for expr, reply in self._actions[action]:
            # print(self._state, expr, expr.eval(self._state))
            if expr.eval(self._state):
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
