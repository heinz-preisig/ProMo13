%!shared indexOrder
%! indexOrder = {"A", "B", "C", "D"};

%!error <Both operands need to be of type MultiDimVar>
%! ## Testing reduceproduct with one operand of wrong type ##
% SETUP
%! S = 20;
%! M = MultiDimVar({"A"}, [5], indexOrder);
% ACTION
%! S * M;

%!error <No common indices>
%! ## Testing reduce product with two vectors of different indices ##
% SETUP
%! V1 = MultiDimVar({"A"}, [5], indexOrder);
%! V2 = MultiDimVar({"B"}, [5], indexOrder);
% ACTION
%! V1 * V2;

%!error <Too many common indices>
%! ## Testing reduce product with two 2D matrices of identical indices ##
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [5, 3], indexOrder);
%! M2 = MultiDimVar({"A", "B"}, [5, 3], indexOrder);
% ACTION
%! M1 * M2;

%!error <Nonconformant arguments>
%! ## Testing reduce product with two 2D matrices of wrong sizes ##
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [5, 3], indexOrder);
%! M2 = MultiDimVar({"B", "C"}, [5, 3], indexOrder);
% ACTION
%! M1 * M2;

%!xtest <## Testing reduceproduct with two vectors ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! V2 = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! expected_output = MultiDimVar({}, [1], indexOrder, [14]);
% ACTION
%! test_output = V1 * V2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with a vector and a 2D matrix (index pos1)##>
% SETUP
%! V = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({"B"}, [2], indexOrder, [22; 28]);
% ACTION
%! test_output = V * M;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with a vector and a 2D matrix (index pos2)##>
% SETUP
%! V = MultiDimVar({"B"}, [3], indexOrder, [1; 2; 3]);
%! M = MultiDimVar({"A", "B"}, [2, 3], indexOrder, [1 3 5; 2 4 6]);
%! expected_output = MultiDimVar({"A"}, [2], indexOrder, [22; 28]);
% ACTION
%! test_output = V * M;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with two 2D matrix (pos1)##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! M2 = MultiDimVar({"A", "C"}, [3, 4], indexOrder, ...
%!                  [1 2 3 4; 5 6 7 8; 9 10 11 12]);
%! expected_output = MultiDimVar({"B", "C"}, [2, 4], indexOrder, ...
%!                               [61 70 79 88; 76 88 100 112]);
% ACTION
%! test_output = M1 * M2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with two 2D matrix (pos2)##>
% SETUP
%! M1 = MultiDimVar({"A", "C"}, [2, 3], indexOrder, [1 3 5; 2 4 6]);
%! M2 = MultiDimVar({"B", "C"}, [4, 3], indexOrder, ...
%!                  [1 5 9; 2 6 10; 3 7 11; 4 8 12]);
%! expected_output = MultiDimVar({"A", "B"}, [2, 4], indexOrder, ...
%!                               [61 70 79 88; 76 88 100 112]);
% ACTION
%! test_output = M1 * M2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with two 2D matrix (pos3)##>
% SETUP
%! M1 = MultiDimVar({"B", "C"}, [3, 2], indexOrder, [1 4; 2 5; 3 6]);
%! M2 = MultiDimVar({"A", "B"}, [4, 3], indexOrder, ...
%!                  [1 5 9; 2 6 10; 3 7 11; 4 8 12]);
%! expected_output = MultiDimVar({"A", "C"}, [4, 2], indexOrder, ...
%!                               [38 83; 44 98; 50 113; 56 128]);
% ACTION
%! test_output = M1 * M2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with two 2D matrix (pos4)##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [2, 3], indexOrder, [1 3 5; 2 4 6]);
%! M2 = MultiDimVar({"B", "C"}, [3, 4], indexOrder, ... 
%!                  [1 4 7 10; 2 5 8 11; 3 6 9 12]);
%! expected_output = MultiDimVar({"A", "C"}, [2, 4], indexOrder, ...
%!                               [22 49 76 103; 28 64 100 136]);
% ACTION
%! test_output = M1 * M2;
% ASSERT
%! assert(isequal(test_output,expected_output))