# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 09:13:00 2017

@author: xa
"""

from game.verb import Verb


class InvalidPreposition(Exception):
    pass

'''
    available actions:
        do
            do something specific
                do puzzle

        apply
            combine two objects with a direction in mind
                use water on fire
                give money to troll

        combine
            combine two objects with no direction in mind
                use water and fire
                combine needle and yarn

        touch
            interact with something

        pet/fondle
            pet soebody
                pet rabbit

        ramble
            let the player say something
                talk
                speak

        have
            unly also usefulls for buffs?
                have faith

        open/close
            interact with doors
                open door
                close door

        take
            appropriate an object and put it in the invetory
                take carrot

        be
            unly also usefulls for buffs?
                be brave

        go
            change room

        utilize
            simply use object
                play piano
                drink water
                use lift

        shout
            one way talkin to somebody or something

        be clever
            be too clever for ones sake
                look behind door


        look
            investigate something
                look at door

        converse
            ask somebody about something
                speak with troll about passage
'''

actions_base_map = {
    'be': {None: {None: 'be'}},
    'have': {None: {None: 'have'}},
    'open': {None: {None: 'open'}},
    'close': {None: {None: 'close'}},
    'do': {None: {None: 'do'}},
    'look': {
        None: {None: 'look'},
        'at': {None: 'look'},
        'behind': {None: 'be clever'},
    },
    'behold': {
        None: {None: 'look'},
    },
    'use': {
        None: {
            None: 'utilize',
            'and': 'combine',
            'on': 'apply',
        },
    },
    'combine': {
        None: {
            None: 'play',
            'and': 'combine',
            'with': 'combine',
        }
    },
    'give': {
        None: {
            None: 'ramble',
            'to': 'apply',
        }
    },
    'play': {
        None: {None: 'utilize'},
        'with': {None: 'utilize'},
    },
    'take': {None: {None: 'take'}},
    'go': {
        None: {None: 'go'},
        'through': {None: 'go'},
        'on': {None: 'ramble'},
    },
    'touch': {None: {None: 'touch'}},
    'pet': {None: {None: 'pet'}},
    'fondle': {None: {None: 'pet'}},
    'speak': {
        None: {None: 'ramble'},
        'with': {
            None: 'shout',
            'about': 'converse',
        }
    },
}


class Action:
    def __init__(self, verb_or_action,
                 local_prep=None, far_prep=None,
                 target=None,
                 predicate=None):

        self.local_prep = None
        self.far_prep = None

        if isinstance(verb_or_action, Action):
            action = verb_or_action
            self.base = action.base
            self.verb = action.verb
            self.local_prep = action.local_prep
            self.far_prep = action.far_prep
            self.target = action.target
            self.predicate = action.predicate
        elif isinstance(verb_or_action, Verb):
            verb = verb_or_action
            self.verb = verb

        if local_prep is not None:
            self.local_prep = local_prep
            if self.local_prep not in self.verb.local_prepositions():
                raise InvalidPreposition()

        if far_prep is not None:
            self.far_prep = far_prep
            if self.far_prep not in self.verb.far_prepositions():
                raise InvalidPreposition()

        self.target = target
        self.predicate = predicate

        self.select_base_for_verb(self.verb.base)

    def __repr__(self):
        if self.target is not None:
            if self.predicate is not None:
                if self.local_prep is not None:
                    return '<{} {} {} {} {}>'.format(self.base,
                                                     self.local_prep,
                                                     self.target,
                                                     self.far_prep,
                                                     self.predicate)
                else:
                    return '<{} {} {} {}>'.format(self.base, self.target,
                                                  self.far_prep,
                                                  self.predicate)
            else:
                if self.local_prep is not None:
                    return '<{} {} {}>'.format(self.base,
                                               self.local_prep, self.target)
                else:
                    return '<{} {}>'.format(self.base, self.target)
        else:
            return '<{}>'.format(self.base)

    def set_target(self, target):
        self.target = target

    def set_predicate(self, predicate):
        self.predicate = predicate

    def set_local_preposition(self, prep):
        self.local_prep = prep
        self.select_base_for_verb(self.verb.base)

    def set_far_preposition(self, prep):
        self.far_prep = prep
        self.select_base_for_verb(self.verb.base)

    def select_base_for_verb(self, verb_base):
        try:
            variants = actions_base_map[verb_base]
            variants = variants[self.local_prep]
            self.base = variants[self.far_prep]
        except KeyError:
            raise InvalidPreposition()

    def swap_taget_and_predicate(self):
        target = self.target
        predicate = self.predicate

        return Action(self, target=predicate, predicate=target)

    # verb emulation
    def infinitive_form(self):
        return self.verb.infinitive_form()

    def past_form(self, form):
        return self.verb.past_form(form)

    def participle_form(self):
        return self.verb.participle_form()

    def ing_form(self):
        return self.verb.ing_form()

    # verb emulatio end

    def present_tense(self, negate, form):
        return self.verb.present_tense(negate, form)

    def present_continuous_tense(self, negate, form):
        return self.verb.present_continuous_tense(negate, form)

    def present_perfect_tense(self, negate, form):
        return self.verb.present_perfect_tense(negate, form)

    def present_perfect_continuous_tense(self, negate, form):
        return self.verb.present_perfect_continuous_tense(negate, form)

    def past_tense(self, negate, form):
        return self.verb.past_tense(negate, form)

    def past_continuous_tense(self, negate, form):
        return self.verb.past_continuous_tense(negate, form)

    def past_perfect_tense(self, negate, form):
        return self.verb.past_perfect_tense(negate, form)

    def past_perfect_continuous_tense(self, negate, form):
        return self.verb.past_perfect_continuous_tense(negate, form)

    def future_tense(self, negate, form):
        return self.verb.future_tense(negate, form)

    def future_continuous_tense(self, negate, form):
        return self.verb.future_continuous_tense(negate, form)

    def future_perfect_tense(self, negate, form):
        return self.verb.future_perfect_tense(negate, form)

    def future_perfect_continuous_tense(self, negate, form):
        return self.verb.future_perfect_continuous_tense(negate, form)

    def conditional_tense(self, negate, form):
        return self.verb.conditional_tense(negate, form)

    def conditional_perfect_tense(self, negate, form):
        return self.verb.conditional_perfect_tense(negate, form)

    def local_prepositions(self):
        if self.local_prep is not None:
            return [self.local_prep]
        return []

    def far_prepositions(self):
        if self.far_prep is not None:
            return [self.far_prep]
        return []

if __name__ == '__main__':
    s = set()

    for u in actions_base_map.values():
        # verb base -> action map
        for v in u.values():
            # action map -> local predicate map
            for w in v.values():
                # local predicate map -> far predicate map
                s.add(w)
    for b in s:
        print(b)
