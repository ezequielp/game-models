#!/usr/bin/python
# -*- coding:utf-8 -*-

from __future__ import division
import networkx as nx
import numpy as np

from itertools import chain

from city import City
from utils import *

def dict2matrix (d):
    return np.matrix (d.values()), d.keys()

class Economy():
    def __init__(self, tradeables):
        self.__city_fields__ = ('inventory','stats')

        self.map         = nx.MultiDiGraph()

        self.total_stock = OrderedDict().fromkeys(sorted(tradeables, key=lambda t: t[0]),0)
        for k in tradeables:
            self.total_stock[k] = 0
        self.__stock_order__ = self.total_stock.keys()

    def __iter__(self):
        return self.city_names()

    def __contains__(self, element):
        return element in self.city_names()

    def stock_order(self):
        '''Get keys order of stock'''
        return dict([(k,i) for i,k in enumerate(self.total_stock.keys())])

    def city_order(self):
        return dict([(k,i) for i,k in enumerate(self.map.nodes_iter())])

    def add_city(self, city):
        # Validate data
        if not isinstance(city,City):
            raise ValueError('Input must be of class City')

        if city in self.city_names():
              raise NameError('City {} already in economy'.format(name))

        for k,v in city.inventory.items():
          if not (k in self.total_stock.keys()):
            # City can't add tradeables
            raise KeyError(k)
          else:
              self.total_stock[k] += v

        self.map.add_node(city.name)
        for p in self.__city_fields__:
            m = sorted(getattr(city,p).items(), key=lambda t: t[0])
            self.map.node[city.name][p] = OrderedDict(m)

    # Getters
    def inventory (self, name, stuff = None):
        ret = self.map.node[name]['inventory']
        if stuff:
            ret = ret[stuff]
        return ret

    def stats (self, name, stat = None):
        ret = self.map.node[name]['stats']
        if stat:
            ret = ret[stat]
        return ret

    def get_all (self, field, item = None):
        if not field in self.__city_fields__:
            raise KeyError(field)
        if item:
            ret = {n[0]: n[1][field][item] for n in self.map.nodes_iter(data=True)}
        else:
            ret = {n[0]: n[1][field] for n in self.map.nodes_iter(data=True)}
        return ret

    def city_names(self):
      return self.map.nodes_iter()

    def calc_stock(self, stuff=None):
        if stuff:
            return sum (x[1]['inventory'][stuff] for x in self.map.nodes_iter(data=True))
        else:
            m = dict()
            for k in self.__stock_order__:
                m[k] = sum (x[1]['inventory'][k] for x in self.map.nodes_iter(data=True))
            return m

    def plot_graph(self, stuff):
        import matplotlib.pyplot as plt
        plt.ion()
        plt.axis('off')
        pos = nx.spring_layout(self.map)
        nx.draw_networkx (self.map, pos=pos, node_size=4000)
        #traffic = dict([(e[0:2],e[2][stuff]) for e in self.map.edges_iter(data=True)])
        #nx.draw_networkx_edge_labels (self.map, pos=pos, edge_labels=traffic, label_pos=0.7)
        plt.title(stuff)

    # Matrix and evolution functions
    def __assemble__(self):
        nx.freeze(self.map)

        self.__city_order__ = self.city_order().keys()

        self.matrix = []
        self.state  = []
        m = self.map
        for k in self.__stock_order__:
#          # This produces a left stochastic matrix
#          A = nx.attr_matrix(self.map, edge_attr=k, rc_order=self.__city_order__)
#          if not all(x == 1 for x in np.sum(A,axis=1)):
#              raise ValueError('Route traffics are not normalized')
#          self.matrix.append(A)

            P = np.matrix([0]*len(self.__city_order__))
            if self.total_stock[k] > 0:
                for j,n in enumerate(self.__city_order__):
                    P[0,j] = m.node[n]['inventory'][k]
                P = P / self.total_stock[k]

            self.state.append(P)

#    def step(self):
#      if not nx.is_frozen(self.map):
#          self.__assemble_chain__()

#      for i,k in enumerate(self.__tradeable_order__):
#          if self.total_stock[k] > 0:
#              p_ = self.state[i] * self.matrix[i]
#              dn = 0.0
#              #dn = s * S_rate (i) - d * D_rate(i); # sources dist
#              n_ = np.maximum(p_ * self.total_stock[k] + dn, 0.0)

#              # Minimize change of total stock due to round off
#              n_ = (np.round(n_), np.round(np.sum(n_ - np.round(n_))))
#              n_ = n_[0] + n_[1]*(n_[0]==n_[0].min());

#              nx.set_node_attributes(self.map, k, \
#                                    dict(zip(self.__market_order__,n_.tolist()[0])))
#              self.total_stock[k] = self.calc_stock(k);
#              self.state[i] = n_ / self.total_stock[k]
# vim: set expandtab tabstop=4 :
