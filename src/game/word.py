#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 08:51:25 2017

@author: xa
"""


class Word:
    def __init__(self, kind, word):
        self._kind = kind
        self._word = word

    def word(self):
        return self._word

    def kind(self):
        return self._kind


class Noun(Word):
    def __init__(self, word, kind='noun', **kwargs):
        super().__init__(kind, word)

        self._indefinite_article = kwargs.pop('indefinite_article', '@default')
        if self._indefinite_article == '@default':
            letter = word[0]
            if letter in ['a', 'e', 'i', 'o', 'u']:
                self._indefinite_article = 'an'
            else:
                self._indefinite_article = 'a'
        self._definite_article = kwargs.pop('definite_article', 'the')
        self._plural = kwargs.pop('plural', None)
        self._is_plural = kwargs.pop('is_plural', False)
        self._is_definite = kwargs.pop('is_definite', True)
        self._is_proper = kwargs.pop('is_proper', False)

        for key in kwargs:
            raise TypeError('got an unexpected argument: {}'.format(key))

    def is_plural(self):
        return self._is_plural

    def is_definite(self):
        return self._is_definite

    def is_proper(self):
        return self._is_proper

    def plural(self):
        if self._is_proper:
            if self._is_plural:
                return self._word
            raise KeyError('no plural form defined for {}'.format(self._word))

        if self._plural is not None:
            return self._plural

        if self._word[-1] == 's':
            return self._word + 'es'
        else:
            return self._word + 's'

    def __repr__(self):
        if self._indefinite_article is not None:
            a = self._indefinite_article
            the = self._definite_article
            out = '{}/{} '.format(the, a)
        else:
            out = ''

        return 'Noun<{}>'.format(out + self._word)


class Adjective(Word):
    def __init__(self, kind, word, **kwargs):
        super().__init__(kind, word)

        self._do_prepend = kwargs.pop('is_proper', True)

        for key in kwargs:
            raise TypeError('got an unexpected argument: {}'.format(key))

    def do_prepend(self):
        return self._do_prepend

    def __repr__(self):
        return 'Adjective<{}>'.format(self._word)


class RegularAdjective(Adjective):
    def __init__(self, word, **kwargs):
        super().__init__('regular', word, **kwargs)


class ColorAdjective(Adjective):
    def __init__(self, word, **kwargs):
        super().__init__('color', word, **kwargs)


class CountingAdjective(Adjective):
    def __init__(self, word, **kwargs):
        super().__init__('counting', word, **kwargs)


class PlacingAdjective(Adjective):
    def __init__(self, word, **kwargs):
        super().__init__('placing', word, **kwargs)


class Compound():
    def __init__(self, description, prepend=True):
        self._description = description
        self._prepend = prepend

    def kind(self):
        return 'compound'

    def word(self):
        return self._description

    def do_prepend(self):
        return self._prepend
