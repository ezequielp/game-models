import networkx as nx
import numpy as np

from collections import OrderedDict as odict
class Economy():
  def __init__(self, tradeables):
      self.map         = nx.MultiDiGraph()
      self.total_stock = odict().fromkeys(tradeables)
      for k in self.total_stock.keys():
        self.total_stock[k] = 0

  def add_market(self, name, **inventory):
      # Validate data
      if name in self.map.nodes():
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
      if not (source in self.map.nodes() and to in self.map.nodes()):
          raise NameError('Markets {} or {} not in economy.'.format(source,to))
      ###

      if isinstance(traffic, tuple):
          traffic = dict(zip(self.total_stock.keys(), traffic))

      self.map.add_edge(source,to,name=name,**traffic)

  def step(self):
    pass

  def __contains__(self, element):
    pass

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
