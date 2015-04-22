#!/usr/bin/python
# -*- coding:utf-8 -*-
import city
import unittest
import numpy as np

NAMES = ["Tatun","Wolfila","Tumunzah","Bardithorp","Pafeld","Gondone",\
          "Heamoor","Caystone","Sasela","Sago"]

class CityTestCase(unittest.TestCase):

    def setUp(self):
        self.cities = list()
        for x in NAMES:
            self.cities.append(city.City(x))

    def test_set(self):
        self.cities[0].set('stats', guts=0,greed=10)
        self.cities[0].set('inventory', wood=1,stone=10)

    def test_order(self):
        c = self.cities[0]
        c.set('stock',wood=1,stone=10)
        idx = c.order('inventory')
        c.set('stats',guts=0,greed=10)
        idx = c.order('stats')

    def test_asrow (self):
        c = self.cities[0]
        c.set('stock',wood=1,stone=10)
        v = np.matrix(np.zeros([1,2]))
        for k,i in c.order('inventory').items():
            v[0,i] = c.stock[k]
        self.assertTrue(np.array_equal(c.asrow('inventory'),v))

        c.set('stats',guts=0,greed=10)
        v = np.matrix(np.zeros([1,2]))
        for k,i in c.order('stats').items():
            v[0,i] = c.stats[k]
        self.assertTrue(np.array_equal(c.asrow('stats'),v))

# vim: set expandtab tabstop=4 :
