#!/usr/bin/python
# -*- coding:utf-8 -*-
import city
import economy
import unittest
import numpy as np

NAMES = ["Tatun","Wolfila","Tumunzah","Bardithorp","Pafeld","Gondone",\
          "Heamoor","Caystone","Sasela","Sago"]

class EconomyTestCase(unittest.TestCase):
    def setUp(self):

        self.tradeables = ('wood','stone')
        self.economy = economy.Economy(tradeables = self.tradeables)
        self.amount = (lambda i: 20*i, lambda i: 2*i+1)
        self.cities = []
        for i,n in enumerate(NAMES):
            c = dict()
            c['name'] = n
            v = dict(zip (self.tradeables,[s(i) for s in self.amount]))
            c['inventory'] = v
            c['pos'] = np.random.rand(1,2)
            c['stats'] = {'greed':np.random.randint(0,10),'guts':np.random.randint(0,10)}
            self.cities.append(c)

    def test_addcity(self):
        for c in self.cities:
            self.economy.add_city(c)
        import pdb
        pdb.set_trace()

    def test_contains(self):
        self.assertTrue(NAMES[0] in self.economy)

    def test_inventory(self):
        for i,c in enumerate(NAMES):
          self.assertEqual(self.amount[0](i), self.economy.inventory(c, "wood"))
          self.assertEqual(self.amount[1](i), self.economy.inventory(c, "stone"))

    def test_calcstock(self):
        s = np.matrix(self.economy.calc_stock().values())
        o = self.economy.stock_order()
        v = np.matrix([[0,0]])
        for k,i in o.items():
            j = self.tradeables.index(k)
            v[0,i] = sum(self.amount[j](z) for z in range(len(NAMES)))

        self.assertTrue(np.array_equal(v, s))

        for k,i in o.items():
            s = self.economy.calc_stock(k)
            self.assertEqual(s,v[0,i])

# vim: set expandtab tabstop=4 :
