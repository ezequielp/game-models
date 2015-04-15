#!/usr/bin/python
# -*- coding:utf-8 -*-

import networkx as nx
import matplotlib.pyplot as plt

cities = ["Tatun","Wolfila","Tumunzah","Bardithorp","Pafeld","Gondone",\
          "Heamoor","Caystone","Sasela","Sago"]
cities.sort()
#sources = ["Lake","River","Wood","Mine","Grassland","Livestock"]

G = nx.barabasi_albert_graph(len(cities), 2)
pos = nx.spring_layout(G)

plt.figure(figsize=(8,8))
# with nodes colored by degree sized by population
node_color=[float(G.degree(v)) for v in G]
nx.draw(G,pos,
     node_color=node_color,
     labels={n:v for n,v in zip(G.nodes(),cities)},
     with_labels=True)


plt.show()
# vim: set tabstop=4 :
