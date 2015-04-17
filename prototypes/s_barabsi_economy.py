#!/usr/bin/python
# -*- coding:utf-8 -*-
from __future__ import division

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

seed = 123456678
np.random.seed(seed)

cities = ["Tatun","Wolfila","Tumunzah","Bardithorp","Pafeld","Gondone",\
          "Heamoor","Caystone","Sasela","Sago"]
cities.sort()
#sources = ["Lake","River","Wood","Mine","Grassland","Livestock"]

G     = nx.barabasi_albert_graph(len(cities), 2, seed)
labels= {n:v for n,v in zip(G.nodes(),cities)}
pos   = nx.spring_layout(G)

plt.figure(figsize=(8,8))
# with nodes colored by degree
#node_color=[float(G.degree(v)) for v in G]
#nx.draw(G, pos, node_color=node_color, labels=labels, with_labels=True)
#plt.show()

# Make the Trade directed
Trade = nx.DiGraph(G);
nx.set_node_attributes(Trade, 'name', labels)
nx.set_node_attributes(Trade, 'pos', pos)

for e in G.edges_iter():
    Trade.add_edge(e[1],e[0])

# Stock and value for each city
stocks = {n:(np.random.randint(0,100),1e3*np.random.rand()) for n in Trade.nodes_iter()}
nx.set_node_attributes(Trade, 'stock', stocks)
total_stock, total_value = np.sum(stocks.values(), axis=0)

# Attitude of the city
city_attributes = ['altruism','greed', 'guts']
att ={n:dict(zip(city_attributes,np.random.randint(0,10,[1,3]).tolist()[0])) \
                                                    for n in Trade.nodes_iter()}
nx.set_node_attributes(Trade, 'stats', att)

# Danger to the roads
dangers = {e:1e3*np.random.rand() for e in Trade.edges_iter()}
nx.set_edge_attributes(Trade, 'danger', dangers)
for c in Trade:
    total_danger = 0
    for n in Trade[c]:
        total_danger += Trade[c][n]['danger']
    for n in Trade[c]:
        Trade[c][n]['danger'] /= total_danger

# Length of the road
for c in Trade:
    for n in Trade[c]:
        Trade[c][n]["length"] = np.sqrt(np.sum((Trade.node[c]["pos"]-Trade.node[n]["pos"])**2))

# Calculate probability of edge
for c in Trade:
    tmp = []
    A   = np.matrix ([[Trade.node[c]['stats'][k]] for k in city_attributes]+[[-1]])
    for n in Trade[c]:
        dx = (Trade.node[n]['stock'][0] - Trade.node[c]['stock'][0])/total_stock
        dv = (Trade.node[n]['stock'][1] - Trade.node[c]['stock'][1])/total_value
        p  = Trade[c][n]['danger']
        l  = Trade[c][n]['length']
        S  = np.matrix([dx,dv,p,l])
        V  = S * A
        Trade[c][n]['flow'] = np.exp (V)
        tmp.append (Trade[c][n]['flow'])
    tmp = np.sum(tmp)
    for n in Trade[c]:
        Trade[c][n]['flow'] /= tmp

# with nodes colored by degree sized by stock
plt.ion()
node_color=[float(Trade.degree(v)) for v in Trade]
node_size=[20*float(Trade.node[v]['stock'][0]) for v in Trade]
nx.draw(Trade, pos, node_size=node_size, node_color=node_color, labels=labels, with_labels=True)

# vim: set tabstop=4 :
