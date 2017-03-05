# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 14:37:50 2017

@author: xa
"""

import collections
import game.word
import game.dictionary


class Predicate():
    def __init__(self, predicates, default=None):
        self.predicates = collections.OrderedDict()
        for predicate in predicates:
            key = predicate.kind()
            self.predicates[key] = predicate
            if default is None:
                default = key
        self.default = default

    def select(self, key_or_keys):
        if isinstance(key_or_keys, list):
            keys = key_or_keys
        else:
            keys = [key_or_keys]

        for key in keys:
            if key in self.predicates:
                return self.predicates[key]
        if self.default is not None and self.default in self.predicates:
            return self.predicates[self.default]

#        for predicate in self.predicates.values():
#            return predicate

    def get_all(self):
        return self.predicates.values()

    def __repr__(self):
        out = []
        for key, value in self.predicates.items():
            out.append('({}) {}'.format(key, value.word()))
        return 'Predicate<{}>'.format(', '.join(out))


def create(list_or_pred, default=None):
    if list_or_pred is None:
        return None

    if not isinstance(list_or_pred, list):
        return list_or_pred

    pred_parts = []
    for part in list_or_pred:
        kind = part.pop('kind')
        if kind == 'adjective':
            word = part.pop('word')
            res = game.dictionary.adjectives[word]
        elif kind == 'pronoun':
            word = part.pop('word')
            res = game.dictionary.pronouns[word]
        elif kind == 'compound':
            word = part.pop('word')
            res = game.word.Compound(word, **part)
        else:
            raise TypeError('unknown predicate kind `{}`'.format(kind))
        pred_parts.append(res)

    return Predicate(pred_parts, default=default)


if __name__ == '__main__':
    import game.dictionary as gd
    from game.word import Compound

    p = Predicate([
        gd.adjectives['first'],
        gd.adjectives['left'],
        gd.adjectives['red'],
        Compound('of greater good')
    ])
    print(p)
    print(p.select('counting').word())
    print(p.select('compound').word())
