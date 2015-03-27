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

redo = false;
## Markov chain with sources.
nT       = 100; # numboer of iteration
n_cities = 3; # numer of cities

# Total amount of stuff
total_stock    = zeros (nT,1);
total_stock(1) = 100;

# Distribution and quantity vectors
n = p = zeros (n_cities,nT);

# Inital distribution of stuff in 3 cities
p(:,1) = (1/n_cities)*ones(n_cities,1);
#p(:,1) = rand(n_cities,1); p(:,1) ./= sum(p(:,1));
n(:,1) = p(:,1) * total_stock (1);

# Transport of stuff among cities (right stochastic)
if redo || !exist ('A')
  A = abs (eye (n_cities) + 0.01*randn (n_cities)); A ./= sum (A);
  redo = false;
endif

# Source emission
S_rate = @(t) round (10*(1 - exp (-t/20)).*exp (-t/50));
# Source connection to cities
#s  = (1/n_cities)*ones(n_cities,1);
#s = rand(n_cities,1); s./= sum (s);
s = [0.7; 0.2; 0.1];

# Sink strength
D_rate = @(t) 10*abs (sin(2*pi*t/60).^7);
#D_rate = @(t) max (min (5*randn () + 5, 10), 0);
# Source connection to cities
d  = (1/n_cities)*ones(n_cities,1);
#d = rand(n_cities,1); d./= sum (d);

# Evolution
for i = 1:nT-1
  p_               = A * p(:,i);       # Cities dist
  dn               = s * S_rate (i) - d * D_rate(i); # sources dist

  n(:,i+1)         = max (p_ * total_stock(i) + dn,0);
  total_stock(i+1) = sum (n(:,i+1));
  p(:,i+1)         = n(:,i+1) / total_stock(i+1);
endfor

figure (1)
clf;

subplot(3,1,1)
plot(n.');
ylabel ("Stuff per city")
legend ({"A","B","C"})
set (gca, "xgrid", "on");

subplot(3,1,2)
plot(total_stock);
ylabel ("total stock")
set (gca, "xgrid", "on");

subplot(3,1,3)
plot(S_rate(1:nT),'-g;Source;', D_rate (1:nT), '-r;Destruction;');
ylabel ("Stuff created and destroyed")
set (gca, "xgrid", "on");
