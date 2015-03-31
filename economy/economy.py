from __future__ import division
import networkx as nx
import numpy as np

from itertools import chain
from collections import OrderedDict as odict

class Economy():
  def __init__(self, tradeables):
      self.map         = nx.MultiDiGraph()
      self.total_stock = odict().fromkeys(tradeables)
      for k in self.total_stock.keys():
        self.total_stock[k] = 0

  def __iter__(self):
      return chain(self.market_names(), self.route_names())
  def __contains__(self, element):
    return element in chain(self.market_names(), self.route_names())

  def add_market(self, name, **inventory):
      # Validate data
      if name in self.market_names():
          raise NameError('Market {} already in economy'.format(name))

      for k,v in inventory.items():
          if not (k in self.total_stock.keys()):
              raise KeyError(k)
      ###

      for k,v in inventory.items():
          self.total_stock[k] += v

      self.map.add_node(name, **inventory)


  def add_route(self, name, source = None, to = None, traffic = None):
      # Validate data
      n = list(self.market_names())
      if source not in n or to not in n:
          raise NameError('Markets {} or {} not in economy.'.format(source,to))
      if name in self.route_names():
          raise NameError('Route {} already exists.'.format(name))
      ###

      tradeables = self.total_stock.keys()
      if isinstance(traffic, tuple):
          traffic = dict(zip(tradeables, traffic))

      # Replace 'rest' by value
          m = self.map
          for k,v in traffic.items():
              if v == 'rest':
                  r = sum([x for e,x in nx.get_edge_attributes(m,k).items() \
                                        if e[0] == source])
                  traffic[k] = 1.0 - r
                  #traffic[k] = np.round((1.0 - r)*1e8) / 1e8

      m.add_edge(source,to,name=name,**traffic)

  def del_route(self, name):
      raise NotImplementedError("ToDo")

  # Getters
  def market(self, name, trade = None):
      ret = self.map.node[name]
      if trade:
        ret = ret[trade]
      return ret

  def route(self, name, trade = None):
      ret = [x[2] for x in self.map.edges_iter(data=True) if x[2]['name']==name][0]
      if trade:
        ret = ret[trade]
      return ret

  def route_names(self):
      return (x[2]['name'] for x in self.map.edges_iter(data=True))

  def market_names(self):
      return self.map.nodes_iter()

  def calc_stock(self, stuff):
      return sum (x[1][stuff] for x in self.map.nodes_iter(data=True))

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
  def __assemble_chain__(self):
      nx.freeze(self.map)

      self.__tradeable_order__ = self.total_stock.keys()
      self.__market_order__    = self.map.nodes()

      self.matrix = []
      self.state  = []
      for k in self.__tradeable_order__:
          # This produces a left stochastic matrix
          A = nx.attr_matrix(self.map, edge_attr=k, rc_order=self.__market_order__)
          if not all(x == 1 for x in np.sum(A,axis=1)):
              raise ValueError('Route traffics are not normalized')
          self.matrix.append(A)

          P = np.matrix([n[1][k]/self.total_stock[k] for n in self.map.nodes_iter(data=True)])
          self.state.append(P)

  def step(self):
      if not nx.is_frozen(self.map):
          self.__assemble_chain__()

      for i,k in enumerate(self.__tradeable_order__):
          p_ = self.state[i] * self.matrix[i]
          dn = 0.0
          #dn = s * S_rate (i) - d * D_rate(i); # sources dist
          n_ = np.round(np.maximum(p_ * self.total_stock[k] + dn, 0.0));
          nx.set_node_attributes(self.map, k, \
                                dict(zip(self.__market_order__,n_.tolist()[0])))
          self.total_stock[k] = self.calc_stock(k);
          self.state[i] = n_ / self.total_stock[k];
