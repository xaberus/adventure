#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 16:41:58 2017

@author: xa
"""

import os
import yaml

from game.word import Noun
from game.word import Pronoun
from game.word import RegularAdjective
from game.word import ColorAdjective
from game.word import CountingAdjective
from game.word import PlacingAdjective


def load_dictionary():
    data_dir = os.path.dirname(__file__)
    dictionary_path = os.path.join(data_dir,
                                   '..',
                                   'data',
                                   'dictionary.yaml')

    nouns = {}
    pronouns = {}
    adjectives = {}

    data = yaml.load(open(dictionary_path, 'r'))

    for noun, args in data['nouns'].items():
        if args is None:
            args = {}
        nouns[noun] = Noun(noun, **args)

    pronoun_map = {
        'possessive': {'is_possessive': True},
    }

    for kind, add in pronoun_map.items():
        for pronoun, args in data['pronouns'][kind].items():
            if args is None:
                args = {}
            for key, value in add.items():
                if key not in args:
                    args[key] = value
            pronouns[pronoun] = Pronoun(pronoun, **args)

    adjective_map = {
        'regular': RegularAdjective,
        'color': ColorAdjective,
        'counting': CountingAdjective,
        'placing': PlacingAdjective,
    }
    for kind in adjective_map.keys():
        for adjective, args in data['adjectives'][kind].items():
            if args is None:
                args = {}
            adj = adjective_map[kind](adjective, **args)
            adjectives[adjective] = adj

    return nouns, pronouns, adjectives

nouns, pronouns, adjectives = load_dictionary()
