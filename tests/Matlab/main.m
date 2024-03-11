function main
  indexOrder = {"A", "B", "C", "D"};
  value1 = cat(3, [1 0 0; 2 1 1], [0 1 0; 0 -1 2], [2 -1 0; 0 0 0]);
  M1 = MultiDimVar({"A", "B", "C"}, [2 3 3], indexOrder, value1);
  M2 = MultiDimVar({"A", "C"}, [2 3], indexOrder, [1 2 3; 4 5 0]);
  M3 = reduceproduct(M1, M2, "C")
  % A = MultiDimVar({"A"}, [3], [1;2;3]);
  % B = MultiDimVar({"B", "A"}, [2, 3], [1 2 3; 4 5 6]);
  % A .* B
  % S = 20;
  % S1 = MultiDimVar({}, [1], [10]);
  % S ./ S1;
  % NS = {[1], [1:3], [1 3]};
  % AS = {[1], [2], [1 3]};
  % S = {1, 2, 3};
  % A = {1, 2, 3};
  % N = {1, 2, 3};
  % % N = mat2cell([1:5]', 5, 1);

  % F = MultiDimVar({"NS", "AS"}, {NS, AS}, reshape(1:24, 6, 4));
  % D = MultiDimVar({"NS", "AS"}, {NS, AS}, reshape(1:24, 6, 4));
  % c = MultiDimVar({"NS"}, {NS}, [0; 0; 0; 1; 0; 0]);
  % fnc = MultiDimVar({"AS"}, {AS}, reshape(1:4, 4, 1));
  % m = MultiDimVar({"N"}, {N}, [1; 2; 3]);
  % V = MultiDimVar({"N"}, {N}, [2; 3; 4]);
  % h = MultiDimVar({"A"}, {A}, [1; 1; 1]);
  % k = MultiDimVar({"N_x_S", "A"}, {NS, A}, reshape(1:18, 6, 3));
  % base = MultiDimVar({"N", "A"}, {N, A}, [1 0 0; 0 0 1]);
  % exponent = MultiDimVar({"N", "A"}, {N, A}, [2 3 4; 0 6 7]);
  % one = MultiDimVar({"A"}, {A}, ones(3, 1));

  % ############################## Transpose #####################################
  % fprintf("Tests for Transpose\n")
  % disp(c')          % The transpose of a 1D is the same 1D (always a column vector)
  % fprintf("========================\n")
  % disp(F')          % The transpose of a 2D behaves as usual
  % ############################ Expand Product ##################################
  % fprintf("Tests for Expand Product\n")
  % a = 3 .* 5        % scalar times scalar
  % fprintf("========================\n")
  % a = 3 .* c;       % scalar times 1D
  % disp(a)
  % fprintf("========================\n")
  % a = F .* 2;       % 2D times scalar
  % disp(a)
  % fprintf("========================\n")
  % a = m .* V;       % 1D times 1D (same indexSet)
  % disp(a)
  % fprintf("========================\n")
  % a = c .* one;       % 1D times 1D (different indexSet)
  % disp(a)
  % fprintf("========================\n")
  % a = F .* D;       % 2D times 2D (same indexSets)
  % disp(a)
  % fprintf("========================\n")
  % a = c .* F;       % 1D times 2D   x .* x,y -> x,y
  % disp(a)
  % fprintf("========================\n")
  % a = fnc .* F;     % 1D times 2D   y .* x,y -> x,y
  % disp(a)
  % fprintf("========================\n")
  % a = F .* fnc;     % 2D times 1D   x,y .* y -> x,y
  % disp(a)
  ############################# Product #############################################
  % fprintf("Tests for Product\n")
  % a = product(m, "N");  % 1D
  % disp(a)
  % fprintf("========================\n")
  % a = product(F, "NS"); % 2D reducing 1st index
  % disp(a)
  % fprintf("========================\n")
  % a = product(F, "AS"); % 2D reducing 2nd index
  % disp(a)
  % fprintf("========================\n")
  % a = product(k, "S"); % 2D reducing 1st inner index
  % disp(a)
  ############################### Power ########################################
  % fprintf("Tests for Power\n")
  % a = base .^ exponent;  % 1D
  % disp(a)
  % fprintf("========================\n")
% endfunction
% function result = indexunion(varargin)
%   result = varargin{1};
%   for i = 2:nargin
%     result = union(result, varargin{i});
%   endfor
% endfunction
  
% - And how do we deal with systems of equations.

% - Should I overload ln, log, sqrt, sin, cos, tan, arcsin, arccos, arctan ....
% - Should I overload min and max
% - Check the difference between classdef and @class folder

