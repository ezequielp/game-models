#!/usr/bin/python
# -*- coding:utf-8 -*-

'''
Copyright (C) 2015 - Juan Pablo Carbajal

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.


@author: Juan Pablo Carbajal <ajuanpi+dev@gmail.com>
'''

from __future__ import division
import networkx as nx
import numpy as np

from itertools import chain

from utils import *

def dict2matrix (d):
    return np.matrix (d.values()), d.keys()

class Economy():
    def __init__(self, tradeables):
        self.__city_fields__  = ('name','inventory','stats', 'pos')
        self.__route_fields__ = ('from','to','name','traffic','length','danger')

        self.map         = nx.MultiDiGraph()

        self.total_stock = OrderedDict().fromkeys(sorted(tradeables, key=lambda t: t[0]),0)
        for k in tradeables:
            self.total_stock[k] = 0
        self.__stock_order__ = self.total_stock.keys()

    def __iter__(self):
        return self.city_names()

    def __contains__(self, element):
        return element in self.city_names()

    #### CITIES ####
    def city_order(self):
        return dict([(k,i) for i,k in enumerate(self.map.nodes_iter())])

    def inventory (self, name, stuff = None):
        ret = {x:self.map.node[name][x] for x in self.map.node[name]['inventory']}
        if stuff:
            ret = ret[stuff]
        return ret

    def stats (self, name, stat = None):
        ret = self.map.node[name]['stats']
        if stat:
            ret = ret[stat]
        return ret

    def get_all_city (self, field, item = None):
        if not field in self.__city_fields__:
            raise KeyError(field)
        if item:
            ret = {n[0]: n[1][field][item] for n in self.map.nodes_iter(data=True)}
        else:
            ret = {n[0]: n[1][field] for n in self.map.nodes_iter(data=True)}
        return ret

    def city_names(self):
        return self.map.nodes_iter()

    def add_city(self, city):
        # Validate data
        for k in city.keys():
            if not k in self.__city_fields__:
                raise KeyError(k)

        if city['name'] in self.city_names():
              raise NameError('City {} already in economy.'.format(city['name']))

        for k,v in city['inventory'].items():
          if not (k in self.total_stock.keys()):
            # City can't add tradeables
            raise KeyError(k)
          else:
              self.total_stock[k] += v

        ## Ideally the data would be stored in a dict in the attribute
        # specified by __city_fields__. But then nx.set_node_attributes
        # (in __assemble__) needs ot be re-implemented, ergo TODO
        m = dict(**city['inventory'])
        m.update(city['stats'])

        self.map.add_node(city['name'], m,\
                                        inventory=city['inventory'].keys(),\
                                        stats=city['stats'].keys(),\
                                        pos=city['pos'])

    #### END CITIES ####

    #### ROUTES ####
    def add_route(self, route):
        # Validate data
        for k in route.keys():
            if not k in self.__route_fields__:
                raise KeyError(k)

        if route['name'] in self.route_names():
            raise NameError('Route {} already exists.'.format(route['name']))

        if route['from'] not in self.city_names() or \
           route['to'] not in self.city_names():
            raise NameError('City {} or {} not in economy.'.format(route['from'],route['to']))

        m = OrderedDict().fromkeys(self.__stock_order__)
        for k in self.__stock_order__:
            if k not in route['traffic'].keys():
                raise KeyError('Traffic for {} missing.'.format(k))
            m[k] = route['traffic'][k]
        ## Ideally the traffic would be stored in a dict in the attribute
        # 'traffic'. But then nx.attr_matrix (in __assemble__) needs ot be
        # re-implemented, ergo TODO
        self.map.add_edge(route['from'], route['to'], m, name=route['name'],\
                                                   traffic=m.keys(),\
                                                   danger=route['danger'],\
                                                   length=route['length'])

    def route_names(self):
        return (n[2]['name'] for n in self.map.edges_iter(data=True))
    #### END ROUTES ####

    #### OTHER ####
    def stock_order(self):
        '''Get keys order of stock'''
        return dict([(k,i) for i,k in enumerate(self.total_stock.keys())])

    def calc_stock(self, stuff=None):
        if stuff:
            if not stuff in self.__stock_order__:
                raise KeyError('Good {} not in stocks.'.format(stuff))
            else:
                return sum (x[1][stuff] for x in self.map.nodes_iter(data=True))
        else:
            m = dict()
            for k in self.__stock_order__:
                m[k] = sum (x[1][k] for x in self.map.nodes_iter(data=True))
            return m

    def plot_graph(self, stuff):
        import matplotlib.pyplot as plt
        plt.ion()
        plt.axis('off')
        pos = nx.spring_layout(self.map)
        nx.draw_networkx (self.map, pos=pos, node_size=4000)
        traffic = dict([(e[0:2],e[2][stuff]) for e in self.map.edges_iter(data=True)])
        nx.draw_networkx_edge_labels (self.map, pos=pos, edge_labels=traffic, label_pos=0.7)
        plt.title(stuff)

    # Matrix and evolution functions
    def __assemble__(self):
        nx.freeze(self.map)

        self.__city_order__ = self.city_order().keys()

        ### TRADE ###
        self.TRADE_matrix = []
        self.TRADE_state  = []
        m = self.map
        for k in self.__stock_order__:
            # This produces a left stochastic matrix
            A = nx.attr_matrix(self.map, edge_attr=k, rc_order=self.__city_order__)
            if not all(x == 1 for x in np.sum(A,axis=1)):
                raise ValueError('Route traffics are not normalized')
            self.TRADE_matrix.append(A)

            P = np.matrix([0]*len(self.__city_order__))
            if self.total_stock[k] > 0:
                for j,n in enumerate(self.__city_order__):
                    P[0,j] = m.node[n]['inventory'][k]
                P = P / self.total_stock[k]

            self.TRADe_state.append(P)
        ### TRADE ###

    def step(self):
        if not nx.is_frozen(self.map):
            self.__assemble_chain__()

        for i,k in enumerate(self.__strock_order__):
            if self.total_stock[k] > 0:
                p_ = self.TRADE_state[i] * self.TRADE_matrix[i]
                dn = 0.0
                #              #dn = s * S_rate (i) - d * D_rate(i); # sources dist
                n_ = np.maximum(p_ * self.total_stock[k] + dn, 0.0)

                # Minimize change of total stock due to round off
                n_ = (np.round(n_), np.round(np.sum(n_ - np.round(n_))))
                n_ = n_[0] + n_[1]*(n_[0]==n_[0].min());

                nx.set_node_attributes(self.map, k, \
                                dict(zip(self.__city_order__,n_.tolist()[0])))
                self.total_stock[k] = self.calc_stock(k);
                self.TRADE_state[i] = n_ / self.total_stock[k]

    def update_trade(self):
        # Calculate probability of route
        Trade = self.map
        for c in Trade:
            # get city mixing vector
            city_stats = Trade.node[c]['stats']
            A   = np.matrix ([Trade.node[c][k] for k in city_stats]+[[-1]])

            tmp = np.zeros([len(self.__stock_order__),1])
            # loop over neighbors of current city
            for n in Trade[c]:
                p  = Trade[c][n]['danger']
                l  = Trade[c][n]['length']
                # Stock difference
                for i,t in enumerate(self.__stock_order__):
                    dx = (Trade.node[n][t] - Trade.node[c][t]) / self.total_stock[i]
                    # Potential gain TODO
                    #dv = (Trade.node[n]['stock'][1] - Trade.node[c]['stock'][1])/total_value
                    W  = np.matrix([dx,dv,p,l])
                    V  = W * A
                    Trade[c][n][t] = np.exp (V)
                    tmp[i] = tmp[i] + Trade[c][n][t]

            # Normalize with softmax
            for n in Trade[c]:
                for i,t in enumerate(self.__stock_order__):
                    Trade[c][n][t] = Trade[c][n][t] / tmp[i]

# vim: set expandtab tabstop=4 :
