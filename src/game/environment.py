# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 13:42:56 2017

@author: xa
"""


import jinja2
import game.filter

env = jinja2.Environment()


def cap_filter(s):
    return s[0].upper() + s[1:]
env.filters['cap'] = cap_filter

def brk_filter(s):
    return '[{}]'.format(s)
env.filters['brk'] = brk_filter

env.filters['inf'] = game.filter.inf_filter
env.filters['ing'] = game.filter.ing_filter
env.filters['prep'] = game.filter.prep_filter
env.filters['xprep'] = game.filter.xprep_filter
env.filters['past'] = game.filter.past_filter


def kind_filter(obj):
    return obj.kind()
env.filters['kind'] = kind_filter

env.filters['namsimp'] = game.filter.namsimp_filter
env.filters['namdefl'] = game.filter.namdefl_filter
env.filters['namdefn'] = game.filter.namdefn_filter
env.filters['namindef'] = game.filter.namindef_filter


@jinja2.contextfilter
def location_filter(data, obj):
    return obj.location().point_to(data)
env.filters['location'] = location_filter


#
#def predobj_filter(obj):
#    pred = obj.pred
#    if pred is not None:
#        pred = pred.name()
#        if obj.proper_name():
#            return ('{} {}'.format(pred, obj.name())).upper()
#        else:
#            return ('the {} {}'.format(pred, obj.name())).upper()
#    else:
#        if obj.proper_name():
#            return obj.name().upper()
#        else:
#            return ('the ' + obj.name()).upper()
#env.filters['predobj'] = predobj_filter
#
#
#def obj_filter(obj):
#    return obj.name().upper()
#env.filters['obj'] = obj_filter
#
#
#def pred_filter(obj):
#    pred = obj.pred
#    if pred is not None:
#        pred = pred.name()
#        return pred.upper()
#    return None
#env.filters['pred'] = pred_filter
#
#
#def point_filter(obj):
#    if obj.point_preposition is not None:
#        return obj.point_preposition.upper()
#    return 'in'.upper()
#env.filters['point'] = point_filter
#
#
#def a_filter(s):
#    c = s[0]
#    if c in ('a', 'e', 'i', 'o', 'u'):
#        return 'an'
#    else:
#        return 'a'
#env.filters['a'] = a_filter
