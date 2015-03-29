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
                  traffic[k] = np.round((1.0 - r)*1e3) / 1e3

      self.map.add_edge(source,to,name=name,**traffic)

  def step(self):
    pass

  def __contains__(self, element):
    pass

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

  # Matrix and evolution functions
  def __assemble_chain__(self):
      self.__tradeable_order__ = self.total_stock.keys()
      self.__market_order__     = self.map.nodes()

      N = len(self.__market_order__)
      K = len(self.__tradeable_order__)
      self.matrix = []
      for k in range(K):
          # This produces a left stochastic matrix
          A = nx.attr_matrix(self.map, 'traffic', rc_order=self.__market_order__)
          if not all(x == 1 for x in np.sum(A,axis=1)):
              raise ValueError('Route traffics are not normalized')

          self.matrix.append(A)
