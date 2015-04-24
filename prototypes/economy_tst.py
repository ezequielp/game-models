#!/usr/bin/python
# -*- coding:utf-8 -*-
from __future__ import division
import economy
import unittest
import numpy as np
import networkx as nx
from utils import *

NAMES = ["Tatun","Wolfila","Tumunzah","Bardithorp","Pafeld","Gondone",\
          "Heamoor","Caystone","Sasela","Sago"]
NAMES.sort()

class EconomyTestCase(unittest.TestCase):
    def setUp(self):
        seed = 123456678
        np.random.seed(seed)
        G     = nx.DiGraph(nx.barabasi_albert_graph(len(NAMES), 2, seed))
        for e in G.edges_iter():
            G.add_edge(e[1],e[0])
        for n in G.nodes_iter():
            G.add_edge(n,n)

        labels= {n:v for n,v in zip(G.nodes(),NAMES)}
        pos   = nx.spring_layout(G)

        self.tradeables = ('wood','stone')
        self.economy = economy.Economy(tradeables = self.tradeables)
        self.amount = (lambda i: 20*i, lambda i: 2*i+1)
        self.cities = []
        for n in G.nodes():
            c = dict()
            c['name'] = labels[n]
            v = dict(zip (self.tradeables,[s(n) for s in self.amount]))
            c['inventory'] = v
            c['pos'] = pos[n]
            c['stats'] = OrderedDict(altruism=np.random.randint(0,10),guts=np.random.randint(0,10))
            self.cities.append(c)

        for c in self.cities:
            self.economy.add_city(c)

        # Roads
        self.routes = []
        danger = 1e3*np.random.rand(len(G.edges()))
        danger = danger / np.sum(danger)
        traffic = np.random.rand(len(G.edges()),len(self.economy.__stock_order__))
        # Normalize
        tmp = np.zeros([len(G.nodes()),traffic.shape[1]])
        for i,e in enumerate(G.edges_iter()):
                tmp[e[0],:] = tmp[e[0],:] + traffic[i,:]
        for i,e in enumerate(G.edges_iter()):
                traffic[i,:] = traffic[i,:] / tmp[e[0],:]

        for i,e in enumerate(G.edges_iter()):
            r = dict()
            r['ini'] = labels[e[0]]
            r['end'] = labels[e[1]]
            r['name'] = '->'.join([r['ini'],r['end']])
            r['traffic'] = dict(zip(self.economy.__stock_order__,traffic[i,:]))
            ini = self.economy.map.node[r['ini']]
            end = self.economy.map.node[r['end']]
            r['length'] = np.sum((end['pos']-ini['pos'])**2)
            r['danger'] = danger[i]
            self.economy.add_route(r)

    def test_contains(self):
        self.assertTrue(NAMES[0] in self.economy)

    def test_inventory(self):
#        import pdb
#        pdb.set_trace()
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

    def test_assemble(self):
        self.economy.__assemble__()

    def test_step(self):
        self.economy.step()

    def test_updatetrade(self):
        self.economy.update_trade()

    def test_cityexport(self):
        self.economy.city_export(NAMES[0],self.tradeables[0])
        self.economy.city_export(NAMES[0])
        self.economy.city_export(stuff=self.tradeables[0])
        self.economy.city_export()

    def test_cityexportok(self):
        for c in self.economy.city_names():
            for s in self.economy.total_stock.keys():
                self.assertTrue(self.economy.is_city_export_ok(c,s))

    def test_addroute_fail(self):
        city = 'test'
        v = dict(zip (self.tradeables,[s(0) for s in self.amount]))
        self.economy.add_city(name=city,\
                              inventory=v,\
                              pos=[0,0],\
                              stats={'altruism':0,'guts':0})
        self.economy.add_route(name='ok', ini=city,\
                                          end=city,\
                                          traffic={'wood':'rest','stone':'rest'},\
                                          length=1,\
                                          danger=1)
        with self.assertRaises(ValueError):
            self.economy.add_route(name='wrong', ini=city,\
                                          end=city,\
                                          traffic={'wood':'rest','stone':'rest'},\
                                          length=1,\
                                          danger=1)

# vim: set expandtab tabstop=4 :
