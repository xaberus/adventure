#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 17:29:26 2017

@author: xa
"""

object_classes = {
}


def get_all_subclasses(cls):
    all_subclasses = []

    all_subclasses.append(cls)

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def register_object_classes(base):
    scls = get_all_subclasses(base)

    for cls in scls:
        object_classes[cls.__name__] = cls
