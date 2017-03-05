# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 23:41:51 2017

@author: xa
"""

import os
import game
from game.util import debug
import pyparsing as pp


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

    boolOperand = pp.Word(pp.alphas)
    boolOperand.setParseAction(BoolOperand)

    boolExpr = pp.infixNotation(boolOperand, [
        ("!", 1, pp.opAssoc.RIGHT, BoolNot),
        ("&", 2, pp.opAssoc.LEFT,  BoolAnd),
        ("|",  2, pp.opAssoc.LEFT,  BoolOr),
    ])

    actionNode = pp.Word(pp.alphas)

    filterNode = pp.Or([pp.Word(pp.alphas), pp.Literal('!')])

    AT = pp.Suppress(pp.Literal("@"))
    LB = pp.Suppress(pp.Literal("["))
    RB = pp.Suppress(pp.Literal("]"))
    SL = pp.Suppress(pp.Literal("/"))
    CM = pp.Suppress(pp.Literal(","))

    gram = pp.And([
        pp.Or([
            pp.Literal('reply'),
            pp.Literal('randomreply'),
        ]).setResultsName('head'),
        AT + actionNode.setResultsName('action'),
        pp.Group(pp.Optional(pp.And([
            LB,
            pp.Optional(pp.And([
                filterNode,
                pp.ZeroOrMore(CM + filterNode),
            ])),
            RB,
        ]))).setResultsName('match_list'),
        pp.Optional(SL + boolExpr).setResultsName('bool_expr'),
    ])

    #############################################

    def __init__(self, state, activation_map, obj):
        self._state = state
        self._actions = {}
        self._activation_map = activation_map
        self._obj = obj

    def _parse_spec(self, spec):
        p = self.gram.parseString(spec, parseAll=True)
        head = str(p['head'])
        action = str(p['action'])
        matches = list(p['match_list'])
        if 'bool_expr' not in p:
            expr = self.BoolOperand(['True'])
        else:
            expr = p['bool_expr'][0]

        return head, action, matches, expr

    def add_action_reply(self, spec, reply_data):
        head, action, matches, expr = self._parse_spec(spec)
        if head == 'reply':
            reply = game.reply.Reply(reply_data)
        elif head == 'randomreply':
            reply = game.reply.RandomReply(reply_data)
        else:
            raise ValueError('unknown reply type `{}`'.format(head))

        if action not in self._actions:
            self._actions[action] = []

        self._actions[action].append((expr, matches, reply))

    def execute_action(self, action, tag, condition):
        base = action.base

        if 'action' in condition:
            if base == condition['action']:
                # action matches entry in activation map
                value = condition.get('value', True)
                self._state[tag] = value
                return True

        elif 'item' in condition:
            cur_item = action.predicate
            wanted_name = condition['item']['name']

            if cur_item.kind() == wanted_name:
                value = condition.get('value', True)
                if self._state[tag] != value:
                    # execute action only on state change
                    self._obj.add_object(cur_item)
                    self._state[tag] = value
                return True

        return False

    def handle_action(self, action, data):
        base = action.base
        debug('[handle action]', base, self._state)
        if base not in self._actions:
            raise game.object.InvalidInteraction()

        out = []
        matched = False
        for expr, matches, reply in self._actions[base]:
            # print(self._state, expr, expr.eval(self._state))
            if expr.eval(self._state):
                # action matches boolean expression

                if len(matches) != 0:
                    if len(matches) != 1 and matches[0] == '!':
                        continue

                    for tag, condition in self._activation_map.items():
                        if tag in matches:
                            # reply matches entry in activation map
                            if self.execute_action(action, tag, condition):
                                out.append(reply.text(data))
                                matched = True

                else:
                    out.append(reply.text(data))

        if not matched:
            for expr, matches, reply in self._actions[base]:
                if expr.eval(self._state):
                    # action matches boolean expression
                    if len(matches) != 1 or matches[0] != '!':
                        continue
                    # default action
                    out.append(reply.text(data))

        if len(out) == 0:
            raise game.object.InvalidInteraction()

        debug('[handled action]', action, self._state)
        raise game.reply.NarratorAnswer(' '.join(out))


class ItemReceiver(game.object.Object):
    def __init__(self, nar, uid, data):
        keys = data.keys()

        actions = []
        activation_map = None

        for key in keys:
            if key.startswith('reply@'):
                actions.append((key, data.pop(key)))
            elif key.startswith('randomreply@'):
                actions.append((key, data.pop(key)))
            elif key == 'activation_map':
                activation_map = data.pop(key)

        super().__init__(nar, uid, data)

        self._arm = ActionReplyMap(self._state, activation_map, self)

        self.objects = set()

        for spec, reply_data in actions:
            self._arm.add_action_reply(spec, reply_data)

    def add_object(self, o):
        o.set_parent(self, relocate=True)
        self.objects.add(o)

    def remove_object(self, obj):
        self.objects.remove(obj)

    def interact(self, action):
        data = {
            'action': action,
            'object': self,
            'item': action.predicate,
        }

        try:
            self._arm.handle_action(action, data)
        except game.object.InvalidInteraction:
            raise self.unknown_replies.complain(data)


if __name__ == '__main__':
    game.registry.register_object_classes(game.object.Object)

    nar = game.narrator.Narrator()
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    game.state.load(nar, data_path, 'test_0.yaml')

    """
        look inventory
        look
        look robot
        look rabbit
        look long carrot
        touch first rabbit
        look second rabbit
        look second rabbit
        pet second rabbit

        give long carrot to bowser
    """

    commands = """
        look inventory
        pet first rabbit
        give long carrot to bowser
        look inventory
        give carrot to bowser
        give carrot to cooper
        look inventory
        go through door
    """

    for cmd in commands.split('\n'):
        nar.interact(cmd.strip())

    print(nar.state().current_room().dump())
