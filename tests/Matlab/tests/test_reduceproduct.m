%!shared indexOrder
%! indexOrder = {"A", "B", "C", "D"};

%!error <Both operands need to be of type MultiDimVar>
%! ## Testing reduceproduct with one operand of wrong type ##
% SETUP
%! S = 20;
%! M = MultiDimVar({"A"}, [5], indexOrder);
% ACTION
%! reduceproduct(S, M, "A");

%!error <No common indices>
%! ## Testing reduce product with two vectors of different indices ##
% SETUP
%! V1 = MultiDimVar({"A"}, [5], indexOrder);
%! V2 = MultiDimVar({"B"}, [5], indexOrder);
% ACTION
%! reduceproduct(V1, V2, "A");

%!error <Wrong number of common indices>
%! ## Testing reduce product with two 2D matrices sharing only one index ##
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [5, 3], indexOrder);
%! M2 = MultiDimVar({"A", "C"}, [5, 3], indexOrder);
% ACTION
%! reduceproduct(M1, M2, "A");

%!error <Nonconformant arguments>
%! ## Testing reduce product with matrices of wrong sizes ##
% SETUP
%! M1 = MultiDimVar({"A", "B", "C"}, [5, 3, 4], indexOrder);
%! M2 = MultiDimVar({"B", "C"}, [6, 3], indexOrder);
% ACTION
%! reduceproduct(M1, M2, "B");

%!test <## Testing reduceproduct with 2D and 3D matrices ##>
% SETUP
%! value1 = cat(3, [1 0 0; 2 1 1], [0 1 0; 0 -1 2], [2 -1 0; 0 0 0]);
%! M1 = MultiDimVar({"A", "B", "C"}, [2 3 3], indexOrder, value1);
%! M2 = MultiDimVar({"A", "C"}, [2 3], indexOrder, [1 2 3; 4 5 0]);
%! expected_output = MultiDimVar({"A", "B"}, [2 3], indexOrder, [7 -1 0; 8 -1 14]);
% ACTION
%! test_output = reduceproduct(M1, M2, "C");
% ASSERT
%! assert(isequal(test_output,expected_output))

