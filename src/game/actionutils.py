# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 22:12:30 2017

@author: xa
"""

import pyparsing as pp
import collections
import game.object
import game.reply
from game.util import debug


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
    PP = pp.Suppress(pp.Literal("|"))

    gram = pp.And([
        pp.Optional(pp.Or([
            pp.Literal('final'),
        ]) + PP).setResultsName('mod'),
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

        if 'mod' not in p:
            mod = ''
        else:
            mod = str(p['mod'])

        return mod, head, action, matches, expr

    def add_action_reply(self, spec, reply_data):
        mod, head, action, matches, expr = self._parse_spec(spec)
        if head == 'reply':
            reply = game.reply.Reply(reply_data)
        elif head == 'randomreply':
            reply = game.reply.RandomReply(reply_data)
        else:
            raise ValueError('unknown reply type `{}`'.format(head))

        if action not in self._actions:
            self._actions[action] = collections.OrderedDict()

        # allow action override
        self._actions[action][spec] = (mod, expr, matches, reply)

    def execute_action(self, action, tag, conditions):
        base = action.base

        for condition in conditions:
            if 'action' in condition:
                if base == condition['action']:
                    # action matches entry in activation map

                    if base == 'take':
                        action.target.take()

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
        for mod, expr, matches, reply in self._actions[base].values():
            # print(self._state, expr, expr.eval(self._state))
            if expr.eval(self._state):
                # action matches boolean expression

                if len(matches) != 0:
                    if len(matches) != 1 and matches[0] == '!':
                        continue

                    for tag, conditions in self._activation_map.items():
                        if tag in matches:
                            # reply matches entry in activation map
                            if self.execute_action(action, tag, conditions):
                                out.append(reply.text(data))
                                matched = True
                                if mod == 'final':
                                    break

                else:
                    out.append(reply.text(data))
                    if mod == 'final':
                        break

        if not matched:
            for mod, expr, matches, reply in self._actions[base].values():
                if expr.eval(self._state):
                    # action matches boolean expression
                    if len(matches) != 1 or matches[0] != '!':
                        continue
                    # default action
                    out.append(reply.text(data))
                    if mod == 'final':
                        break

        if len(out) == 0:
            raise game.object.InvalidInteraction()

        debug('[handled action]', action, self._state)
        raise game.reply.NarratorAnswer(' '.join(out))
