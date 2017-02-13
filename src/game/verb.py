# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 00:17:14 2017

@author: xa
"""

shortcuts = {
    None: 'infinitive',
    'i': 'infinitive',
    'inf': 'infinitive',
    'infinitive': 'infinitive',

    'p': 'past',
    'pst': 'past',
    'past': 'past',

    'pr': 'participle',
    'prt': 'participle',
    'participle': 'participle',

    'pre': 'preposition',
    'preposition': 'preposition',
}

verbs = {}


class Verb:
    preposition = None

    def __format__(self, spec):
        if spec is None or spec == '':
            spec = 'infinitive'

        if spec not in shortcuts:
            raise KeyError('unknown format `{}`'.format(spec))

        spec = shortcuts[spec]

        if spec == 'infinitive':
            return self.infinitive()
        elif spec == 'past':
            return self.past()
        elif spec == 'participle':
            return self.participle()
        elif spec == 'preposition':
            return self.preposition()
        else:
            raise KeyError('unknown format `{}`'.format(spec))

    def infinitive(self):
        pass

    def past(self):
        pass

    def participle(self):
        pass

    def preposition(self):
        return self.prep


# verb forms
class RegularVerb(Verb):
    def __init__(self, base, prep=None):
        self.base = base
        self.prep = prep

    def infinitive(self):
        return self.base

    def past(self):
        if self.base[-1] != 'e':
            return self.base + 'ed'
        else:
            return self.base + 'd'

    def participle(self):
        if self.base[-1] != 'e':
            return self.base + 'ed'
        else:
            return self.base + 'd'


class IrregularVerb(Verb):
    def __init__(self, base, past, pariciple, prep=None):
        self.base = base
        self.prep = prep
        self.past_form = past
        self.pariciple_form = pariciple

    def infinitive(self):
        return self.base

    def past(self):
        return self.past_form

    def participle(self):
        return self.participle_form


def _define_verb(base, past=None, pariciple=None, prep=None):
    if past is None and pariciple is None:
        verbs[base] = RegularVerb(base, prep=prep)
    else:
        verbs[base] = IrregularVerb(base, past, pariciple, prep=prep)

_define_verb('look', prep='at')
_define_verb('behold', 'beheld', 'beheld')
_define_verb('use')
_define_verb('open')
_define_verb('close')
# _define_verb('cook')
_define_verb('take', 'took', 'taken')
_define_verb('take', 'took', 'taken')
_define_verb('go', 'went', 'gone')
_define_verb('speak', 'spoke', 'spoken', prep='with')
_define_verb('talk', prep='to')
_define_verb('touch')
# _define_verb('ring', 'rang', 'rung')
