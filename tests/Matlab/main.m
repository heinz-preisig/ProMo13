function main
  NS = {[1], [1:3], [1 3]};
  AS = {[1], [2], [1 3]};
  S = {1, 2, 3};
  A = {1, 2, 3};
  N = {1, 2, 3};
  % N = mat2cell([1:5]', 5, 1);

  F = MultiDimVar({"NS", "AS"}, {NS, AS}, reshape(1:24, 6, 4));
  c = MultiDimVar({"NS"}, {NS}, [0; 0; 0; 1; 0; 0]);
  fnc = MultiDimVar({"AS"}, {AS}, reshape(1:4, 4, 1));
  % lambda = MultiDimVar(reshape(1:3, 3, 1), {"S"}, {S});
  % p = MultiDimVar(reshape(1:3, 3, 1), {"N"}, {N});
  % fv = MultiDimVar(reshape(1:3, 3, 1), {"A"}, {A});
  % m1 = MultiDimVar(reshape(1:9, 3, 3), {"N", "A"}, {N, A});
  % m2 = MultiDimVar(reshape(1:9, 3, 3), {"A", "N"}, {A, N});

  disp(reduceproduct(F, "AS", fnc))
  F = sparse(F);
  fnc = sparse(fnc);
  disp(reduceproduct(F, "AS", fnc))

  % disp(product(fnc, "AS"))
  % % g = MultiDimVar({}, {}, 9.8);
  % % disp(g)
  % disp(F)
  % disp(product(F, "AS"))
  % size(product(F, "AS"))

endfunction
function result = indexunion(varargin)
  result = varargin{1};
  for i = 2:nargin
    result = union(result, varargin{i});
  endfor
endfunction
  
% - And how do we deal with systems of equations.

% - Should I overload ln, log, sqrt, sin, cos, tan, arcsin, arccos, arctan ....
% - Should I overload min and max
% - Check the difference between classdef and @class folder

