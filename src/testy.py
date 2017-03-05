# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 23:41:51 2017

@author: xa
"""

import os
import yaml
import collections
import game.name
import game.object
import game.room
import game.door


class Narrator:
    def require_uid_state(self, uid):
        return {}


class Proto:
    def __init__(self, data):
        self._data = collections.OrderedDict(data)

    def create(self, nar):
        raise NotImplementedError()

    def merge_data(self, m):
        if m is None:
            return

        def _merge(d, m):
            for k, v in m.items():
                if k in d:
                    if isinstance(d[k], dict):
                        _merge(d[k], v)
                    else:
                        d[k] = v
                else:
                    print(k, v)
                    d[k] = v

        _merge(self._data, m)


class LocationProto(Proto):
    pass


class ObjectProto(Proto):
    def create(self, nar):
        uid = self._data.pop('uid')
        return game.object.create(nar, uid, self._data)


class RoomProto(ObjectProto):
    pass


class MyLoader(yaml.Loader):
    names = {
        'Bowser': {'name': 'Bowser'}
    }

    def __init__(self, *args, **kwargs):
        cur_path = os.path.dirname(__file__)
        self.data_path = os.path.join(cur_path, 'data')

        super().__init__(*args, **kwargs)

        self.add_constructor('!include', self._include)
        self.add_constructor('!Name', self._contruct_name)
        self.add_constructor('!Object', self._construct_object)
        self.add_constructor('!Location', self._construct_location)
        self.add_constructor('!Room', self._construct_room)

    def _include(self, loader, node):
        try:
            m = loader.construct_mapping(node, deep=True)
            path = m.pop('path')
        except yaml.MarkedYAMLError:
            path = loader.construct_scalar(node)
            m = None

        file_path = os.path.join(self.data_path, path)
        data = yaml.load(open(file_path, 'r'), Loader=self.__class__)
        data.merge_data(m)
        return data

    def _contruct_name(self, loader, node):
        try:
            data = loader.construct_mapping(node, deep=True)
            return game.name.create(data)
        except yaml.MarkedYAMLError:
            word = loader.construct_scalar(node)
            return game.name.names[word]

    def _construct_location(self, loader, node):
        return LocationProto(loader.construct_pairs(node, deep=True))

    def _construct_object(self, loader, node):
        return ObjectProto(loader.construct_pairs(node, deep=True))

    def _construct_room(self, loader, node):
        return RoomProto(loader.construct_pairs(node, deep=True))


#class Room(yaml.YAMLObject):
#    yaml_tag = '!Room'
#
#    @classmethod
#    def from_yaml(cls, loader, node):
#        m = collections.OrderedDict(loader.construct_pairs(node))
#        return m


#class Name(yaml.YAMLObject):
#    yaml_tag = '!Name'

"""



"""

if __name__ == '__main__':
    game.registry.register_object_classes(game.object.Object)

    data_path = os.path.join(os.path.dirname(__file__), 'data')
    level_path = os.path.join(data_path, 'test_0.yaml')
    o = yaml.load(open(level_path, 'r'), Loader=MyLoader)

    nar = Narrator()

    for room in o['rooms']:
        print(room.create(nar))
