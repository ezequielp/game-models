#!/usr/bin/python
# -*- coding:utf-8 -*-
import numpy as np
from collections import OrderedDict

class UniqueDict(OrderedDict):

    def __setitem__(self, key, value):
        if key not in self:
            OrderedDict.__setitem__(self, key, value)
        else:
            raise KeyError("Key already exists")

class City():
    ''' a class for cities with lower case names '''

    def __init__(self, name):

        self.name = name

        self.stock  = UniqueDict()
        self.stats  = UniqueDict()

    ##### Getters
    def order (self,field):
        '''Get keys order of field'''
        d = getattr(self,field)
        return dict([(k,i) for i,k in enumerate(d.keys())])

    def stats_order (self):
        '''Get stats key orders '''
        return self.order('stats')

    def stock_order (self):
        '''Get stock key orders '''
        return self.order('stock')

    def as_row (self, field):
        '''Get any dict values as row matrix '''
        return np.matrix (getattr(self,field).values())

    def get_stock (self):
        '''Get stock values as row matrix '''
        return self.as_row('stock')

    def get_stats (self):
        '''Get stats values as row matrix '''
        return self.as_row('stats')

    ##### Setters
    def set (self, field, **values):
        getattr(self,field).update(values)

    def set_stock (self, **values):
        self.set('stock',**values)

    def set_stats (self, **values):
        self.set('stats',**values)


# vim: set expandtab tabstop=4 :
