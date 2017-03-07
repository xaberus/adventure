#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 15:03:12 2017

@author: xa
"""

from game.name import Name


def inf_filter(verb):
    p = verb.local_prepositions()
    out = verb.infinitive_form()
    if len(p) > 0:
        out = '{} {}'.format(out, p[0])
    return out


def ing_filter(verb):
    p = verb.local_prepositions()
    out = verb.ing_form()

    if len(p) > 0:
        out = '{} {}'.format(out, p[0])
    return out


def prep_filter(verb):
    return verb.preposition()


def xprep_filter(verb):
    p = verb.far_prepositions()
    if len(p) > 0:
        return p[0]


def past_filter(verb, negate=False, form='1sng'):
    p = verb.local_prepositions()
    out = verb.past_tense(negate, form)
    if len(p) > 0:
        out = '{} {}'.format(out, p[0])
    return out


def namsimp_filter(obj):
    if not isinstance(obj, Name):
        obj = obj.name()
    return obj.simple_form([])


# TODO: comment
def namdefl_filter(obj):
    if not isinstance(obj, Name):
        obj = obj.name()
    return obj.default_form([])


def namdefn_filter(obj):
    if not isinstance(obj, Name):
        obj = obj.name()
    return obj.definite_form([])


def namindef_filter(obj):
    if not isinstance(obj, Name):
        obj = obj.name()
    return obj.indefinite_form([])


def namplural_filter(obj):
    if not isinstance(obj, Name):
        obj = obj.name()
    return obj.plural_form([])
