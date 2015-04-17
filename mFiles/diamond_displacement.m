## Copyright (C) 2015 - Juan Pablo Carbajal
##
## This program is free software; you can redistribute it and/or modify
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

## source: http://www.gameprogrammer.com/fractal.html
order=4;
N=2^order+1;
[x y] = meshgrid (1:N);
z = rand(N);

function [s d n] = square_diamond_step (x)
  # centers
  s = mean(x);
  dx = (max(x(:,1))-min(x(:,1)))/2;
  dy = (max(x(:,2))-min(x(:,2)))/2;
  # diamons
  d = s + [0 1; 1 0; 0 -1; -1 0].*[dx dy];
  n = cell (4,1);
  # new squares
  n{1} = [x(1,:); d([3 4],:); s];
  n{2} = [d(3,:); x(2,:); s; d(2,:)];
  n{3} = [d(4,:); s; x(3,:); d(1,:)];
  n{4} = [s; d([2 1],:); x(4,:)];
endfunction

function show (s,d,h,N)
  ind = sub2ind ([N,N],s(:,1),s(:,2));
  set(h(ind),'markerfacecolor','k');
  pause(0.1)
  set(h(ind),'markerfacecolor',[0.5 1 0.5]);
  if d
    set(h(ind),'markerfacecolor',[1 0.5 0.5]);
    ind = sub2ind([N,N],d(:,1),d(:,2));
    set(h(ind),'markerfacecolor','k');
    pause(0.3)
    set(h(ind),'markerfacecolor',[0 0.8 0.8]);
  endif
endfunction

sub = {[1,1 ; N,1 ; 1,N; N,N]};

## this is only to plot
flag_plot=true;
if flag_plot
  #close all

  figure(1)
  clf
  graphics_toolkit(1,'fltk');
  #set(gcf,'visible','off')
  hold on
  h = arrayfun (@(i,j)plot(i,j),x(:),y(:));
  set(h,'marker','o','markeredgecolor','k','markersize',12);
  axis tight;
  axis off
  #set(gcf,'visible','on')
  hold off

  show (sub{1},[],h,N)

#  figure(2)
#  hm = mesh(x,y,z);
#  set(hm,'edgecolor','k')
#  axis tight;
#  v = axis();
#  axis([v(1:4) -0.5 0.5])
endif

# some parameters
scale =1;
r=0.9;
rr=@(n) 2*rand(n)-1;

for i=1:order
  scale /= 2^(r);
  # average over square points
  avg = cellfun(@(x)mean(z(sub2ind([N,N],x(:,1),x(:,2)))),sub);

  [sc, d, n] = cellfun (@square_diamond_step, sub,"UniformOutput",false);

  # change center values
  ind = cellfun(@(x)sub2ind([N,N],x(1),x(2)),sc);
  z(ind) = avg + scale*rr(size(ind));

  #change diamonds
  indd = cell2mat(cellfun(@(x)sub2ind([N,N],x(:,1),x(:,2)),d,"UniformOutput",false));
  z(indd) = (reshape(scale*rr(size(indd)),4,length(ind)) + z(ind).')(:);

  # hack to smooth
  z(ind) = mean(reshape(z(indd),4,length(ind)));

  sub = vertcat(n{:});
  if flag_plot
    cellfun (@(x,y)show(x,y,h,N),sc,d);
  #  set(hm,'zdata',z);
  endif

endfor
axis tight
