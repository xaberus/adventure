# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 13:42:56 2017

@author: xa
"""


import jinja2


env = jinja2.Environment()


def inf_filter(verb):
    p = verb.preposition()
    out = verb.infinitive()
    if p is not None:
        out = '{} {}'.format(out, p)
    return out.upper()
env.filters['inf'] = inf_filter


def ing_filter(verb):
    p = verb.preposition()
    out = verb.infinitive() + 'ing'
    if p is not None:
        out = '{} {}'.format(out, p)
    return out.upper()
env.filters['ing'] = ing_filter


def prep_filter(verb):
    return verb.preposition()
env.filters['prep'] = prep_filter


def past_filter(verb):
    p = verb.preposition()
    out = verb.past()
    if p is not None:
        out = '{} {}'.format(out, p)
    return out.upper()
env.filters['past'] = past_filter


def predobj_filter(obj):
    pred = obj.pred
    if pred is not None:
        pred = pred.name()
        return ('{} {}'.format(pred, obj.name())).upper()
    else:
        return obj.name().upper()
env.filters['predobj'] = predobj_filter


def obj_filter(obj):
    return obj.name().upper()
env.filters['obj'] = obj_filter


def pred_filter(obj):
    pred = obj.pred
    if pred is not None:
        pred = pred.name()
        return pred.upper()
    return None
env.filters['pred'] = pred_filter


def a_filter(s):
    c = s[0]
    if c in ('a', 'e', 'i', 'o', 'u'):
        return 'an'
    else:
        return 'a'
env.filters['a'] = a_filter
