#!/usr/bin/python
# -*- coding:utf-8 -*-
import numpy as np
from utils import *

class City():
    ''' a class for cities with lower case names '''

    def __init__(self, name):

        self.name = name

        self.inventory  = OrderedDict()
        self.stats      = OrderedDict()

    ##### Getters
    def order (self,field):
        '''Get keys order of field'''
        d = getattr (self,field)
        return dict([(k,i) for i,k in enumerate(d.keys())])

    def asrow (self, field):
        '''Get any dict values as row matrix '''
        return np.matrix (getattr(self,field).values())

    ##### Setters
    def set (self, field, **values):
        getattr(self,field).update(values)

# vim: set expandtab tabstop=4 :
