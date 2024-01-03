%!shared indexOrder
%! indexOrder = {"A", "B", "C", "D"};


%!error <Both operands need to be of type MultiDimVar>
%! ## Testing expandproduct with operands of the wrong type ##
% SETUP
%! S = 20;
%! V = MultiDimVar({"A"}, [5], indexOrder);
% ACTION
%! expandproduct(S, V);

%!error <Common indices found>
%! ## Testing expandproduct with two vectors with same indices ##
% SETUP
%! V1 = MultiDimVar({"A"}, [3], indexOrder);
%! V2 = MultiDimVar({"A"}, [3], indexOrder);
% ACTION
%! expandproduct(V1, V2);

%!xtest <## Testing expandproduct with two vectors ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! V2 = MultiDimVar({"B"}, [3], indexOrder, [1; 2; 3]);
%! expected_output = MultiDimVar({"A", "B"}, [3, 3], indexOrder, ...
%!                               [1 2 3; 2 4 6; 3 6 9]);
% ACTION
%! test_output = expandproduct(V1, V2);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing expandproduct with a vector and a 2D matrix (pos1) ##>
% SETUP
%! V = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! M = MultiDimVar({"B", "C"}, [2, 2], indexOrder, [1 2; 3 4]);
%! expected_value = cat(3, [1 3; 2 6; 3 9], [2 4; 4 8; 6 12]);
%! expected_output = MultiDimVar({"A","B","C"}, [3, 2, 2], indexOrder, ...
%!                               expected_value);
% ACTION
%! test_output = expandproduct(V, M);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing expandproduct with a vector and a 2D matrix (index ordering) ##>
% SETUP
%! V = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! M = MultiDimVar({"B", "C"}, [2, 2], indexOrder, [1 2; 3 4]);
%! expected_value = cat(3, [1 3; 2 6; 3 9], [2 4; 4 8; 6 12]);
%! expected_output = MultiDimVar({"A","B", "C"}, [2, 2, 3], indexOrder, ...
%!                               expected_value);
% ACTION
%! test_output = expandproduct(M, V);
% ASSERT
%! assert(isequal(test_output,expected_output))




