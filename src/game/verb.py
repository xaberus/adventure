# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 00:17:14 2017

@author: xa
"""

import collections
from game.util import collect

verbs = {}
xverbs = {}


class XVerb:
    def infinitive_form(self):
        return self.base

    def past_form(self, form):
        return self.base + 'ed'

    def participle_form(self):
        return self.base + 'ed'

    def ing_form(self):
        return self.base + 'ing'

    def present_tense(self, negate, form):
        if form == '3sng':
            out = self.base + 's'
        else:
            out = self.base

        if negate:
            return '{} not'.format(out)
        else:
            return out

    def present_continuous_tense(self, negate, form):
        aux_verb = xverbs['be']
        out = aux_verb.present_tense(negate, form)
        if negate:
            return '{} not {}'.format(out, self.ing_form())
        else:
            return '{} {}'.format(out, self.ing_form())

    def present_perfect_tense(self, negate, form):
        aux_verb = xverbs['have']
        out = aux_verb.present_tense(negate, form)
        if negate:
            return '{} not {}'.format(out, self.participle_form())
        else:
            return '{} {}'.format(out, self.participle_form())

    def present_perfect_continuous_tense(self, negate, form):
        aux_verb = xverbs['have']
        aux_part = xverbs['be'].participle_form()
        out = aux_verb.present_tense(negate, form)
        if negate:
            return '{} {} not {}'.format(out, aux_part, self.ing_form())
        else:
            return '{} {} {}'.format(out, aux_part, self.ing_form())

    def past_tense(self, negate, form):
        if negate:
            return '{} not'.format(self.past_form(form))
        else:
            return self.past_form(form)

    def past_continuous_tense(self, negate, form):
        aux_verb = xverbs['be']
        out = aux_verb.past_form(form)
        if negate:
            return '{} not {}'.format(out,  self.ing_form())
        else:
            return '{} {}'.format(out,  self.ing_form())

    def past_perfect_tense(self, negate, form):
        aux_verb = xverbs['have']
        out = aux_verb.past_form(form)
        if negate:
            return '{} not {}'.format(out,  self.participle_form())
        else:
            return '{} {}'.format(out,  self.participle_form())

    def past_perfect_continuous_tense(self, negate, form):
        aux_verb = xverbs['have']
        aux_part = xverbs['be'].participle_form()
        out = aux_verb.past_tense(negate, form)
        if negate:
            return '{} {} not {}'.format(out, aux_part, self.ing_form())
        else:
            return '{} {} {}'.format(out, aux_part, self.ing_form())

    def future_tense(self, negate, form):
        if negate:
            return 'will not {}'.format(self.infinitive_form())
        else:
            return 'will {}'.format(self.infinitive_form())

    def future_continuous_tense(self, negate, form):
        aux_verb = xverbs['be']
        out = aux_verb.infinitive_form()
        if negate:
            return 'will not {} {}'.format(out, self.ing_form())
        else:
            return 'will {} {}'.format(out, self.ing_form())

    def future_perfect_tense(self, negate, form):
        aux_verb = xverbs['have']
        out = aux_verb.infinitive_form()
        if negate:
            return 'will not {} {}'.format(out, self.participle_form())
        else:
            return 'will {} {}'.format(out, self.participle_form())

    def future_perfect_continuous_tense(self, negate, form):
        aux_verb = xverbs['have']
        aux_part = xverbs['be'].participle_form()
        out = aux_verb.infinitive_form()
        if negate:
            return 'will not {} {} {}'.format(out, aux_part,
                                              self.ing_form())
        else:
            return 'will {} {} {}'.format(out, aux_part,
                                          self.ing_form())

    def conditional_tense(self, negate, form):
        if negate:
            return 'would not {}'.format(self.infinitive_form())
        else:
            return 'would {}'.format(self.infinitive_form())

    def conditional_perfect_tense(self, negate, form):
        aux_verb = xverbs['have']
        out = aux_verb.infinitive_form()
        if negate:
            return 'would not {} {}'.format(out, self.participle_form())
        else:
            return 'would {} {}'.format(out, self.participle_form())

    def local_prepositions(self):
        return []

    def far_prepositions(self):
        return []


class XBe(XVerb):
    base = 'be'
    present_map = {
        '1sng': 'am',
        '2sng': 'are',
        '3sng': 'is',
        '1plr': 'are',
        '2plr': 'are',
        '3plr': 'are',
    }
    past_map = {
        '1sng': 'was',
        '2sng': 'was',
        '3sng': 'was',
        '1plr': 'were',
        '2plr': 'were',
        '3plr': 'were',
    }

    def past_form(self, form):
        return self.past_map[form]

    def participle_form(self):
        return 'been'

    def ing_form(self):
        return 'being'

    def present_tense(self, negate, form):
        if negate:
            return '{} not'.format(self.present_map[form])
        else:
            return self.present_map[form]

xverbs['be'] = XBe()


class XHave(XVerb):
    base = 'have'
    present_map = {
        '1sng': 'have',
        '2sng': 'have',
        '3sng': 'has',
        '1plr': 'have',
        '2plr': 'have',
        '3plr': 'have',
    }

    def past_form(self, form):
        return 'had'

    def participle_form(self):
        return 'had'

    def ing_form(self):
        return 'having'

    def present_tense(self, negate, form):
        if negate:
            return '{} not'.format(self.present_map[form])
        else:
            return self.present_map[form]

xverbs['have'] = XHave()


class XDo(XVerb):
    base = 'do'

    def past_form(self, form):
        return 'did'

    def participle_form(self):
        return 'done'

    def present_tense(self, negate, form):
        if form == '3sng':
            out = 'does'
        else:
            out = self.base
        if negate:
            return '{} not'.format(out)
        else:
            return out

xverbs['do'] = XDo()


class XPlay(XVerb):
    base = 'play'

xverbs['play'] = XPlay()


class XUse(XVerb):
    base = 'use'

    def ing_form(self):
        return 'using'

xverbs['use'] = XUse()


class XLook(XVerb):
    base = 'look'

xverbs['look'] = XLook()


class XBehold(XVerb):
    base = 'behold'

    def past_form(self, form):
        return 'beheld'

    def participle_form(self):
        return 'beheld'

xverbs['behold'] = XBehold()


class XOpen(XVerb):
    base = 'open'

xverbs['open'] = XOpen()


class XClose(XVerb):
    base = 'close'

xverbs['close'] = XClose()


class XTake(XVerb):
    base = 'take'

    def past_form(self, form):
        return 'took'

    def participle_form(self):
        return 'taken'

xverbs['take'] = XTake()


class XGo(XVerb):
    base = 'go'

    def past_form(self, form):
        return 'went'

    def participle_form(self):
        return 'gone'

xverbs['go'] = XGo()


class XSpeak(XVerb):
    base = 'speak'

    def past_form(self, form):
        return 'spoke'

    def participle_form(self):
        return 'spoken'

xverbs['speak'] = XSpeak()


class XTalk(XVerb):
    base = 'talk'

xverbs['talk'] = XSpeak()


class XTouch(XVerb):
    base = 'touch'

xverbs['touch'] = XTouch()

########################################
########################################


class Verb:
    preposition = None

    def infinitive(self):
        pass

    def past(self):
        pass

    def participle(self):
        pass

    def ing(self):
        out = self.infinitive()
        if out not in ['use']:
            return out + 'ing'
        else:
            return out[:-1] + 'ing'

    def preposition(self):
        return self.prep

    def extra_prepositions(self):
        return self.xprep


# verb forms
class RegularVerb(Verb):
    def __init__(self, base, prep=None, xprep=None):
        self.base = base
        self.prep = prep
        self.xprep = xprep

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
    def __init__(self, base, past, participle, prep=None, xprep=None):
        self.base = base
        self.prep = prep
        self.xprep = xprep
        self.past_form = past
        self.participle_form = participle

    def infinitive(self):
        return self.base

    def past(self):
        return self.past_form

    def participle(self):
        return self.participle_form


def _define_verb(base, past=None, participle=None, **kwargs):
    if past is None and participle is None:
        verbs[base] = RegularVerb(base, **kwargs)
    else:
        verbs[base] = IrregularVerb(base, past, participle, **kwargs)

_define_verb('look', prep='at')
_define_verb('behold', 'beheld', 'beheld')
_define_verb('use', xprep=['with', 'on', 'and'])
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

if __name__ == '__main__':
    verb = xverbs['use']

    todo = [
        ('I', '1sng'),
        ('you', '2sng'),
        ('he/she/it', '3sng'),
        ('we', '1plr'),
        ('you', '2plr'),
        ('they', '3plr'),
    ]

    methods = [
        'present_tense',
        'present_continuous_tense',
        'present_perfect_tense',
        'present_perfect_continuous_tense',
        'past_tense',
        'past_continuous_tense',
        'past_perfect_tense',
        'past_perfect_continuous_tense',
        'future_tense',
        'future_continuous_tense',
        'future_perfect_tense',
        'future_perfect_continuous_tense',
        'conditional_tense',
        'conditional_perfect_tense',
    ]

    for method_name in methods:
        print('\n(( {} ))'.format(' '.join(method_name.split('_')[0:-1])))
        outputs = collections.OrderedDict()
        method = getattr(verb, method_name)
        for pronoun, form in todo:
            out = method(False, form)
            collect(outputs, out, pronoun)
        for k, v in outputs.items():
            print(', '.join(set(v)), k)
