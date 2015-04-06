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

## Gillespie’s algorithm for stochastic reactions.
# Code derived from 
# http://www.lamfa.u-picardie.fr/asch/f/t/anglais/ressources/chem_reac.pdf

# Stoichiometric matrix
# Each column is a reaction (will be parsed from file)
# A + B --c1--> C
# C --c2--> A + B
# C --c3--> B + D

V = [[-1; -1; 1; 0] [1; 1; -1; 0] [0; 1; -1; 1]];

### Parameters and Initial Conditions
X    = zeros(4,1);
X(1) = 20; # quantity of A
X(2) = 10; # quantity of B

c(1) = 1e-2; c(2) = 1e-4; c(3) = 1e-1; # rates

t      = 0;
tfinal = 50;
Y = X;
T = t;

### Simulation 
while t < tfinal
  # Update propensities
  a(1) = c(1)*X(1)*X(2);
  a(2) = c(2)*X(3);
  a(3) = c(3)*X(3);

  # Update time
  asum = sum (a);
  tau  = log (1/rand) / asum;
  
  # Find th eindex of the reaction that will occur
  j = min (find (rand < cumsum(a/asum)));

  # Update quantities
  X = X + V(:,j);
  t = t + tau;
  
  # Record
  Y(:,end+1) = X;
  T(end+1)   = t;
end

plot (T, Y.');
legend ({"A","B","C","D"})

