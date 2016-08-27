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

from operator import itemgetter
from collections import OrderedDict, defaultdict, namedtuple
from itertools import groupby
__route_fields__ = ('start', 'end', 'traffic', 'length', 'danger')
__city_fields__ = ('stats', 'pos', 'inventory')


def dict2matrix(d):
    return np.matrix(d.values()), d.keys()


def is_within_eps(value):
    return np.abs(value) <= np.sqrt(np.spacing(1))


def extract_route(attr):
    return tuple(attr.get(k, None) for k in __route_fields__)


def extract_city(attr):
    return tuple(attr.get(k, None) for k in __city_fields__)


def validate_routes(routes, existing_markets, valid_goods):
    route_names = [name for name, _, _, _ in routes]
    repeated = [name for name, _, _, _ in routes if route_names.count(name) > 1]

    if len(repeated) > 0:
        repeated = ', '.join(repeated)
        raise NameError('Repeated route names in definition: {}.'.format(repeated))

    market_names = [market.name for market in existing_markets]

    for name, start, end, traffic in routes:
        if start not in market_names:
            raise NameError('City {} not in economy.'.format(start))

        if end not in market_names:
            raise NameError('City {} not in economy'.format(end))

        for good in traffic._asdict().keys():
            if good not in valid_goods:
                raise KeyError('Tradeable {} of route {} undefined.'.format(good, name))

        try:
            for g in valid_goods:
                getattr(traffic, g)
        except:
            raise ValueError("{} does not contain {}".format(traffic, g))

def validate_markets(markets, valid_goods):
    names = [market.name for market in markets]
    repeated = [name for name in set(names) if names.count(name) > 1]

    if len(repeated) > 0:
        repeated = ', '.join(repeated)
        raise NameError('Repeated market names in definition: {}.'.format(repeated))

    valid_goods = set(valid_goods)
    for name, inventory in markets:
        invalid_inventory = set(inventory._asdict().keys()) - valid_goods
        if len(invalid_inventory) > 0:
            # City can't add tradeables
            raise KeyError("City {} has invalid inventories {}"
                           .format(name, invalid_inventory))

iEconomyBP = namedtuple("EconomyBlueprint", ('tradeables', 'markets', 'routes'))
iMarketBP = namedtuple("MarketBlueprint", ('name', 'tradeables'))
iRouteBP = namedtuple("RouteBlueprint", ('name', 'start', 'end', 'traffic'))


def validate(bp):
    tradeables, markets, routes = bp
    validate_markets(markets, tradeables)
    validate_routes(routes, markets, tradeables)


def replace_in_route(route, replacements):
    return iRouteBP(
        route.name,
        route.start,
        route.end,
        route.traffic._replace(**replacements)
    )


def autocomplete(bp):
    ud = namedtuple("UsefulData", ['name', 'start', 'good', 'qty'])
    # We detect routes that need autocompletion
    # extract data from the route if any outgoing good needs to be completed
    to_autocomplete = [ud(name, start, good, qty)
                       for name, start, end, traffic in bp.routes
                       for good, qty in traffic._asdict().items()]

    if not to_autocomplete:
        return bp

    # Group outgoing goods by starting town and good name
    def grouping(x):
        return (x.start, x.good)

    to_autocomplete = sorted(to_autocomplete, key=grouping)
    outgoing = groupby(to_autocomplete, grouping)
    replacements = {}
    for info, group in outgoing:
        group = list(group)
        try:
            route_name = next(n for n, _ ,_ ,q in group if q == 'rest')
        except StopIteration, e:
            continue

        town_name, good_name = info
        total = sum(qty for _, _, _, qty in group if qty != 'rest')

        if route_name not in replacements:
            replacements[route_name] = dict()

        replacements[route_name][good] = 1 - total

    # Return new BT with 'rest' replaced by the total
    return iEconomyBP(
        bp.tradeables,
        bp.markets,
        tuple(route if route.name not in replacements else
              replace_in_route(route, replacements[route.name])
              for route in bp.routes))


class EconomyBlueprintFactory():
    """Create a valid description of an economy.

    This Factory creates a blueprint valid for constructing an economy.
    It provides validation logic plus parsing of shortcuts like the 'rest' keyword.
    """
    def __init__(self, blueprintData=iEconomyBP((), (), ())):
        self.bp = blueprintData

    def trades(self, tradeables):
        bp = self.bp
        return EconomyBlueprintFactory(
            iEconomyBP(
                bp.tradeables + tuple(tradeables),
                bp.markets,
                bp.routes))

    def hasMarket(self, name, inventory):
        market = iMarketBP(name, inventory)
        bp = self.bp
        return EconomyBlueprintFactory(
            iEconomyBP(
                bp.tradeables,
                bp.markets + (market, ),
                bp.routes))

    def hasRoute(self, name, start, end, traffic):
        """This blueprint has a unidirectional route to the economy.

        Args:
            name: The name of the route.
            start: The name of the market that sells on this route.
            end: The name of the market that buys on this route.
            traffic: Dictionary-like structure detailing the goods being traded on this
                route in the form: { good: volume|'rest' } .
                When used as a value, the keyword 'rest' means that this route will trade
                all the surplus of good from town 'start' to town 'end'
        """
        route = iRouteBP(name, start, end, traffic)
        bp = self.bp
        return EconomyBlueprintFactory(
            iEconomyBP(
                bp.tradeables,
                bp.markets,
                bp.routes + (route,)))

    def blueprint(self):
        validate(self.bp)
        return autocomplete(self.bp)

    def build(self):
        return Economy(self.blueprint())


class Economy():
    """A simulation of the trading aspect of an economy.

    Economy is an Observable built from a blueprint, which is assumed to be consistent.
    Economy on itself needs to observe a tick stream to emit events.
    """

    # This will be the stable interface
    def __init__(self, blueprint):

        # contains the good for which export is already fully defined
        self.export_complete = defaultdict(set)

        self.map = nx.MultiDiGraph()

        self.total_stock = OrderedDict().fromkeys(sorted_tradeables, 0)
        self.existing_goods = self.total_stock.keys()

    def __iter__(self):
        return self.city_names()

    def __contains__(self, element):
        return element in self.city_names()

    def stock(self, name, good=None):
        ret = {x: self.map.node[name][x] for x in self.map.node[name]['inventory']}
        if good:
            ret = ret[good]
        return ret

    def traffic(self, name, good=None):
        return next(x[2]['traffic'][good]
                    for x in self.map.edges_iter(data=True)
                    if x[2]['name'] == name)

    def stats(self, name, stat=None):
        ret = self.map.node[name]['stats']
        if stat:
            ret = ret[stat]
        return ret

    def add_market(self, name, inventory, **city):
        if callable(inventory._asdict):
            inventory = inventory._asdict()

        city.update({'inventory': inventory})
        validate_market(name, city, self.city_names(), self.existing_goods)
        # Validate data

        for k, v in inventory.items():
            self.total_stock[k] += v

        stats, pos, _ = extract_city(city)

        # Ideally the data would be stored in a dict in the attribute
        # specified by tradeables. But then nx.set_node_attributes
        # (in __assemble__) needs ot be re-implemented, ergo TODO
        m = dict(**inventory)

        self.map.add_node(name, attr_dict=m,
                          inventory=inventory.keys(),
                          stats=stats,
                          pos=pos)

    def add_route(self, name, start, end, traffic, **attr):
        """Adds a unidirectional route to the economy.

        Args:
            name: The name of the route.
            start: The name of the market that sells on this route.
            end: The name of the market that buys on this route.
            traffic: Dictionary-like structure detailing the goods being traded on this
                route in the form: { good: volume|'rest' } .
                When used as a value, the keyword 'rest' means that this route will trade
                all the surplus of good from town 'start' to town 'end'
            attr: Other data that can be added to the route for tagging purposes.

        Returns:
            None
        """
        if callable(traffic._asdict):
            traffic = traffic._asdict()

        attr.update({'start': start, 'end': end, 'traffic': traffic})
        validate_route(name, attr, self.city_names(), self.route_names(),
                       self.existing_goods)

        start, end, traffic, length, danger = extract_route(attr)

        for good in traffic.keys():
            if good in self.export_complete[start]:
                raise ValueError('Export of {} out of city {} is already fully defined.'
                                 .format(good, start))

        # Goods not given are not traded over the route
        traffic.setdefault(0)

        # If an entry on traffic is 'rest', it is replaced by
        # the corresponding value and the export completed
        # TODO: move logic to just before assembling the matrix to stop from "completing"
        if 'rest' in traffic.values():
            for k, v in traffic.items():
                if v == 'rest':
                    self.export_complete[start].add(k)
                    r = np.sum(x for e, x in nx.get_edge_attributes(self.map, k).items()
                               if e[0] == start)
                    traffic[k] = 1.0 - r

        # TODO: Ideally the traffic would be stored in a dict in the attribute
        # 'traffic'. But then nx.attr_matrix (in __assemble__) needs ot be
        # re-implemented

        self.map.add_edge(start, end,
                          attr_dict=traffic,
                          traffic=traffic,
                          name=name,
                          danger=danger,
                          length=length)

    # This interface is not really stable, it is for internal use or not final
    def get_all_city(self, field, item=None):
        if field not in self.city_fields:
            raise KeyError(field)
        if item:
            ret = {n[0]: n[1][field][item] for n in self.map.nodes_iter(data=True)}
        else:
            ret = {n[0]: n[1][field] for n in self.map.nodes_iter(data=True)}
        return ret

    def city_names(self):
        return list(self.map.nodes_iter())

    def city_export(self, name=None, stuff=None):
        # FIXME multigraph!
        ret = dict()
        if name and stuff:
            for n in self.map[name]:
                ret[n] = self.map[name][n][0][stuff]
        elif name and not stuff:
            for n in self.map[name]:
                neigh = self.map[name][n][0]
                ret[n] = {k:v for (k,v) in neigh.iteritems() if k in neigh['traffic']}
        elif not name and stuff:
            for c in self.map.nodes_iter():
                ret[c] = self.city_export(c, stuff)
        else:
            for c in self.map.nodes_iter():
                ret[c] = {s:self.city_export(c,s) for s in self.existing_goods}
        return ret

    def is_city_export_ok(self,name,stuff):
        return is_within_eps(1.0-np.sum(self.city_export(name,stuff).values()))
    
    def city_order(self):
        return dict([(k,i) for i, k in enumerate(self.map.nodes_iter())])

    def route_names(self):
        return (n[2]['name'] for n in self.map.edges_iter(data=True))

    #### END ROUTES ####

    def stock_order(self):
        '''Get keys order of stock'''
        return dict([(k,i) for i,k in enumerate(self.total_stock.keys())])

    def calc_stock(self, stuff=None):
        if stuff:
            if not stuff in self.existing_goods:
                raise KeyError('Good {} not in stocks.'.format(stuff))
            else:
                return sum (x[1][stuff] for x in self.map.nodes_iter(data=True))
        else:
            m = dict()
            for k in self.existing_goods:
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
        for k in self.existing_goods:
            # This produces a left stochastic matrix
            A = nx.attr_matrix(self.map, edge_attr=k, rc_order=self.__city_order__)
            if not all(is_within_eps(1.0-x) for x in np.sum(A,axis=1)):
                print np.sum(A,axis=1)
                raise ValueError('Route traffics are not normalized')
            self.TRADE_matrix.append(A)

            P = np.matrix([0]*len(self.__city_order__))
            if self.total_stock[k] > 0:
                for j,n in enumerate(self.__city_order__):
                    P[0,j] = m.node[n][k]
                P = P / self.total_stock[k]

            self.TRADE_state.append(P)
        ### TRADE ###

    def step(self):
        if not nx.is_frozen(self.map):
            self.__assemble__()

        for i,k in enumerate(self.existing_goods):
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
            A   = np.matrix ([Trade.node[c][k] for k in city_stats]+[-1]).T

            tmp = np.zeros([len(self.existing_goods),1])
            # loop over neighbors of current city
            for n in Trade[c]:
                # FIXME: Multidigraph!
                d  = Trade[c][n][0]['danger']
                l  = Trade[c][n][0]['length']
                for i,t in enumerate(self.existing_goods):
                    # Stock difference
                    dx = (Trade.node[n][t] - Trade.node[c][t]) / self.total_stock[t]
                    # Potential gain TODO
                    #dv = (Trade.node[n]['stock'][1] - Trade.node[c]['stock'][1])/total_value
                    #W  = np.matrix([dx,dv,d,l])

                    # FIXME order of city stats!
                    W  = np.matrix([dx,d,l])
                    V  = W * A
                    Trade[c][n][0][t] = np.exp (V)
                    tmp[i] = tmp[i] + Trade[c][n][0][t]

            # Normalize with softmax
            for n in Trade[c]:
                for i,t in enumerate(self.existing_goods):
                    Trade[c][n][0][t] = Trade[c][n][0][t] / tmp[i]

# vim: set expandtab tabstop=4 :
