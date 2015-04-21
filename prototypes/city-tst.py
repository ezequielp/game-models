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

    def test_setstock(self):
        self.cities[0].set_stock(wood=1,stone=10)

    def test_setstats(self):
        self.cities[0].set_stats(guts=0,greed=10)

    def test_set(self):
        self.cities[0].set('stats', guts=0,greed=10)
        self.cities[0].set('stock', wood=1,stone=10)

    def test_stockorder(self):
        c = self.cities[0]
        c.set_stock(wood=1,stone=10)
        idx = c.stock_order()

    def test_asrow (self):
        c = self.cities[0]
        c.set_stock(wood=1,stone=10)
        v = np.matrix(np.zeros([1,2]))
        for k,i in c.stock_order().items():
            v[0,i] = c.stock[k]
        self.assertTrue(np.array_equal(c.as_row('stock'),v))

        c.set_stats(guts=0,greed=10)
        v = np.matrix(np.zeros([1,2]))
        for k,i in c.stats_order().items():
            v[0,i] = c.stats[k]
        self.assertTrue(np.array_equal(c.as_row('stats'),v))

# vim: set expandtab tabstop=4 :
