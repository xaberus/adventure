#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 20:05:07 2017

@author: xa
"""

import os
import yaml
import game.dictionary
import game.word
import game.predicate
from game.util import debug


class Name():
    def simple_form(self, keys):
        raise NotImplementedError()

    def default_form(self, keys):
        raise NotImplementedError()

    def definite_form(self, keys):
        raise NotImplementedError()

    def indefinite_form(self, keys):
        raise NotImplementedError()

    def plural_form(self, keys):
        raise NotImplementedError()

    def predicate(self, keys):
        pred = None
        if self.pred is not None:
            pred = self.pred.select(keys)

        return pred

    def drop_predicates(self):
        raise NotImplementedError()

    def __repr__(self):
        out = self.default_form([])
        return '{}<{}>'.format(self.__class__.__name__, out)

    def variants(self):
        raise NotImplementedError()


class ObjectName(Name):
    def __init__(self, noun, pred=None):
        assert isinstance(noun, game.word.Noun)
        assert pred is None or isinstance(pred, game.predicate.Predicate)

        self.noun = noun
        self.pred = pred

    def a_compose(self, *args):
        out = []

        letter = None
        for arg in args:
            if arg is not None:
                if letter is None:
                    letter = arg[0]
                    if letter in ['a', 'e', 'i', 'o', 'u']:
                        out.append('an')
                    else:
                        out.append('a')
                out.append(arg)
        return ' '.join(out)

    def the_compose(self, *args, proper=False):
        if proper:
            out = ['The']
        else:
            out = ['the']
        for arg in args:
            if arg is not None:
                out.append(arg)
        return ' '.join(out)

    def simple_compose(self, *args):
        out = []
        for arg in args:
            if arg is not None:
                out.append(arg)
        return ' '.join(out)

    def simple_form(self, keys):
        pred = self.predicate(keys)
        compose = self.simple_compose

        if pred is not None:
            if pred.do_prepend():
                return compose(pred.word(), self.noun.word()).lower()
            else:
                return compose(self.noun.word(), pred.word()).lower()
        else:
            return compose(self.noun.word()).lower()

    def default_form(self, keys):
        if self.noun.is_definite():
            return self.definite_form(keys)
        else:
            return self.indefinite_form(keys)

    def definite_form(self, keys):
        proper = self.noun.is_proper()
        pred = self.predicate(keys)
        if pred is not None:
            if pred.do_prepend():
                return self.the_compose(pred.word(), self.noun.word(),
                                        proper=proper)
            else:
                return self.the_compose(self.noun.word(), pred.word(),
                                        proper=proper)
        else:
            return self.the_compose(self.noun.word(), proper=proper)

    def indefinite_form(self, keys=[]):
        pred = self.predicate(keys)
        if not self.noun.is_plural():
            compose = self.a_compose
        else:
            compose = self.simple_compose

        if pred is not None:
            if pred.do_prepend():
                return compose(pred.word(), self.noun.word()).lower()
            else:
                return compose(self.noun.word(), pred.word()).lower()
        else:
            return compose(self.noun.word()).lower()

    def plural_form(self, keys):
        pred = self.predicate(keys)
        plural = self.noun.plural()
        if pred is not None:
            if pred.do_prepend():
                return self.simple_compose(pred.word(), plural)
            else:
                return self.simple_compose(plural, pred.word())
        else:
            return self.simple_compose(plural)

    def drop_predicates(self):
        return self.__class__(self.noun, pred=None)

    def variants(self):
        def mkidn(*args):
            t = []
            for arg in args:
                for part in arg.split():
                    t.append(part.lower())
            return tuple(t)

        out = []

        out.append(mkidn(self.noun.word()))

        if self.pred is not None:
            for pred in self.pred.get_all():
                if pred.do_prepend():
                    idn = mkidn(pred.word(), self.noun.word())
                    out.append(idn)
                else:
                    idn = mkidn(self.noun.word(), pred.word())
                    out.append(idn)
        return out


class ProperName(ObjectName):
    def default_form(self, keys):
        return self.definite_form(keys)

    def simple_compose(self, *args):
        out = []
        for arg in args:
            if arg is not None:
                l = arg.split()
                for p in l:
                    out.append(p[0].upper() + p[1:])
        return ' '.join(out)

    def definite_form(self, keys):
        pred = self.predicate(keys)
        if pred is not None:
            if pred.do_prepend():
                return self.simple_compose(pred.word(), self.noun.word())
            else:
                return self.simple_compose(self.noun.word(), pred.word())
        else:
            return self.simple_compose(self.noun.word())

    def indefinite_form(self, keys=[]):
        raise TypeError('proper names no indefinite forms')


def create(data):
    if isinstance(data, str):
        return names[data]

    if not isinstance(data, dict):
        return data

    # debug('[load name]', data)

    default_pred = data.pop('default_predicate', None)
    pred_data = data.pop('predicates', None)
    is_proper = data.pop('is_proper', False)

    pred = game.predicate.create(pred_data, default_pred)

    noun = data.pop('noun')
    if isinstance(noun, str):
        noun = game.dictionary.nouns[noun]

    if is_proper or noun.is_proper():
        cls = ProperName
        default_pred = None
    else:
        cls = ObjectName

    for key in data:
        raise TypeError('got an unexpected argument: {}'.format(key))

    name = cls(noun, pred)

    return name


def load_dictionary():
    data_dir = os.path.dirname(__file__)
    dictionary_path = os.path.join(data_dir,
                                   '..',
                                   'data',
                                   'dictionary.yaml')

    names = {}

    data = yaml.load(open(dictionary_path, 'r'))

    for name, args in data['names'].items():
        default_pred = args.pop('default_predicate', None)
        pred_data = args.pop('predicates', None)
        pred = game.predicate.create(pred_data, default_pred)
        word = args.pop('noun', None)
        if word is None:
            word = name
            noun = game.word.Noun(word, **args)
        else:
            noun = game.dictionary.nouns[word]
            for key in args:
                raise TypeError('got an unexpected argument: {}'.format(key))

        names[name] = create({
            'noun': noun,
            'predicates': pred,
        })

    return names

names = load_dictionary()


if __name__ == '__main__':
    import game.dictionary as gd
    from game.word import Compound
    from game.predicate import Predicate

    d = ObjectName(gd.nouns['door'], pred=Predicate([
        gd.adjectives['glass'],
        gd.adjectives['left'],
    ]))
    print(d.definite_form([]))
    print(d.indefinite_form([]))
    print(d.plural_form([]))
    print(d.variants())

    d = ObjectName(gd.nouns['mouse'], pred=Predicate([
        gd.adjectives['white'],
    ]))
    print(d.definite_form([]))
    print(d.indefinite_form([]))
    print(d.plural_form([]))
    print(d.variants())

    d = ObjectName(gd.nouns['rabbit'], pred=Predicate([
        gd.adjectives['white'],
    ]))
    print(d.definite_form([]))
    print(d.indefinite_form([]))
    print(d.plural_form([]))
    print(d.variants())

    d = names['Bowser']
    print(d.default_form([]))
    print(d.variants())

    d = ObjectName(gd.nouns['potion'], pred=Predicate([
        Compound('of greater good', prepend=False),
    ]))
    print(d.default_form([]))
    print(d.definite_form([]))
    print(d.indefinite_form([]))
    print(d.variants())
