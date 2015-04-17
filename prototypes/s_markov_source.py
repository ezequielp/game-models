## Copyright (C) 2015 - Juan Pablo Carbajal
##
## This progrm is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>.

## Author: Juan Pablo Carbajal <ajuanpi+dev@gmail.com>

from __future__ import division
import numpy as np
from scipy import sparse
import matplotlib.pyplot as plt

redo = False;

## Markov chain with sources.
nT       = 100; # numboer of iteration
n_cities = 4; # numer of cities

# Total amount of stuff
total_stock    = np.zeros([nT,1]);
total_stock[0] = 100;

# Distribution and quantity vectors
n = np.zeros([n_cities,nT]);
p = np.zeros([n_cities,nT]);

# Inital distribution of stuff in 3 cities
p[:,0] = np.array([1/n_cities]*n_cities);
#p[:,0] = np.rand(n_cities,1); p[:,0] ./= np.sum(p[:,0]));
n[:,0] = p[:,0] * total_stock [0];

# Transport of stuff among cities (right stochastic)
if redo or ('A' not in locals()):
    A = abs(np.eye(n_cities) + 0.01*np.random.randn(n_cities));
    A = A / np.sum(A,axis=0);
    redo = False;

# Source emission
def S_rate(t): return np.round(10*np.multiply(1-np.exp(-t/20),np.exp(-t/50)));
# Source connection to cities
s = np.array([0.7, 0.2, 0.1, 0.0]);

# Sink strength
def D_rate(t): return 10*abs(np.sin(2*np.pi*t/60)**7);
# np.max(np.min (5*np.random.randn() + 5, 10), 0);
# Source connection to cities
d  = np.array([1/n_cities]*n_cities);
#d = rand(n_cities,1); d./= sum (d);

# Evolution
for i  in range (nT-1):
    p_ = A.dot(p[:,i])       # Cities dist
    dn = s * S_rate (i) - d * D_rate(i); # sources dist

    n[:,i+1]         = np.maximum(p_ * total_stock[i] + dn, 0);
    total_stock[i+1] = np.sum(n[:,i+1], axis=0);
    p[:,i+1]         = n[:,i+1] / total_stock[i+1];

plt.ion()
plt.figure(1)
plt.clf();

plt.subplot(3,1,1)
plt.plot(n.T)
plt.ylabel("Stuff per city")
names = ("City "+chr(ord('A')+i) for i in range(n_cities))
plt.legend(list(names))

plt.subplot(3,1,2)
plt.plot(total_stock)
plt.ylabel("total stock")

plt.subplot(3,1,3)
plt.plot(S_rate(np.arange(nT)),'g',D_rate(np.arange(nT)),'r');
plt.ylabel ("Stuff created and destroyed")
plt.legend(["created","destroyed"])
