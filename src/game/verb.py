# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 00:17:14 2017

@author: xa
"""

import collections
from game.util import collect

verbs = {}


class Verb:
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
        aux_verb = verbs['be']
        out = aux_verb.present_tense(negate, form)
        if negate:
            return '{} not {}'.format(out, self.ing_form())
        else:
            return '{} {}'.format(out, self.ing_form())

    def present_perfect_tense(self, negate, form):
        aux_verb = verbs['have']
        out = aux_verb.present_tense(negate, form)
        if negate:
            return '{} not {}'.format(out, self.participle_form())
        else:
            return '{} {}'.format(out, self.participle_form())

    def present_perfect_continuous_tense(self, negate, form):
        aux_verb = verbs['have']
        aux_part = verbs['be'].participle_form()
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
        aux_verb = verbs['be']
        out = aux_verb.past_form(form)
        if negate:
            return '{} not {}'.format(out,  self.ing_form())
        else:
            return '{} {}'.format(out,  self.ing_form())

    def past_perfect_tense(self, negate, form):
        aux_verb = verbs['have']
        out = aux_verb.past_form(form)
        if negate:
            return '{} not {}'.format(out,  self.participle_form())
        else:
            return '{} {}'.format(out,  self.participle_form())

    def past_perfect_continuous_tense(self, negate, form):
        aux_verb = verbs['have']
        aux_part = verbs['be'].participle_form()
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
        aux_verb = verbs['be']
        out = aux_verb.infinitive_form()
        if negate:
            return 'will not {} {}'.format(out, self.ing_form())
        else:
            return 'will {} {}'.format(out, self.ing_form())

    def future_perfect_tense(self, negate, form):
        aux_verb = verbs['have']
        out = aux_verb.infinitive_form()
        if negate:
            return 'will not {} {}'.format(out, self.participle_form())
        else:
            return 'will {} {}'.format(out, self.participle_form())

    def future_perfect_continuous_tense(self, negate, form):
        aux_verb = verbs['have']
        aux_part = verbs['be'].participle_form()
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
        aux_verb = verbs['have']
        out = aux_verb.infinitive_form()
        if negate:
            return 'would not {} {}'.format(out, self.participle_form())
        else:
            return 'would {} {}'.format(out, self.participle_form())

    def local_prepositions(self):
        return []

    def far_prepositions(self):
        return []


class Be(Verb):
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

verbs['be'] = Be()


class Have(Verb):
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

verbs['have'] = Have()


class Do(Verb):
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

verbs['do'] = Do()


class Play(Verb):
    base = 'play'

    def local_prepositions(self):
        return ['with']

verbs['play'] = Play()


class Use(Verb):
    base = 'use'

    def ing_form(self):
        return 'using'

    def far_prepositions(self):
        return ['with', 'at', 'and']

verbs['use'] = Use()


class Combine(Verb):
    base = 'combine'

    def ing_form(self):
        return 'combining'

    def far_prepositions(self):
        return ['with', 'and']

verbs['combine'] = Combine()


class Give(Verb):
    base = 'give'

    def ing_form(self):
        return 'giving'

    def far_prepositions(self):
        return ['to']

verbs['give'] = Give()


class Look(Verb):
    base = 'look'

    def local_prepositions(self):
        return ['at', 'behind']

verbs['look'] = Look()


class Behold(Verb):
    base = 'behold'

    def past_form(self, form):
        return 'beheld'

    def participle_form(self):
        return 'beheld'

verbs['behold'] = Behold()


class Open(Verb):
    base = 'open'

verbs['open'] = Open()


class Close(Verb):
    base = 'close'

    def ing_form(self):
        return "closing"

verbs['close'] = Close()


class Take(Verb):
    base = 'take'

    def past_form(self, form):
        return 'took'

    def participle_form(self):
        return 'taken'

    def far_prepositions(self):
        return ['to']

    def ing_form(self):
        return "taking"

verbs['take'] = Take()


class Go(Verb):
    base = 'go'

    def past_form(self, form):
        return 'went'

    def participle_form(self):
        return 'gone'

    def local_prepositions(self):
        return ['through', 'to']

verbs['go'] = Go()


class Speak(Verb):
    base = 'speak'

    def past_form(self, form):
        return 'spoke'

    def participle_form(self):
        return 'spoken'

    def local_prepositions(self):
        return ['with']

    def far_prepositions(self):
        return ['about']

verbs['speak'] = Speak()


class Talk(Verb):
    base = 'talk'

    def local_prepositions(self):
        return ['to']

verbs['talk'] = Talk()


class Touch(Verb):
    base = 'touch'

verbs['touch'] = Touch()


class Pet(Verb):
    base = 'pet'

    def ing_form(self):
        return 'petting'

verbs['pet'] = Pet()


class Fondle(Verb):
    base = 'fondle'

    def ing_form(self):
        return 'fondling'

verbs['fondle'] = Fondle()


if __name__ == '__main__':
    verb = verbs['look']

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
