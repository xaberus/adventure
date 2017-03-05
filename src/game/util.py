#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 11:15:56 2017

@author: xa
"""

def collect(d, k, v):
    if k not in d:
        d[k] = []
    a = d[k]
    if v not in a:
        a.append(v)


def debug(*args, **kwargs):
    # print(*args, **kwargs)
    pass
