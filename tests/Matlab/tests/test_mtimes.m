%!error <Both operands need to be of type MultiDimVar>
%! ## Testing reduceproduct with one operand of wrong type ##
% SETUP
%! S = 20;
%! M = MultiDimVar({"A"}, [5]);
% ACTION
%! S * M;

%!error <No common indices>
%! ## Testing reduce product with two vectors of different indices ##
% SETUP
%! V1 = MultiDimVar({"A"}, [5]);
%! V2 = MultiDimVar({"B"}, [5]);
% ACTION
%! V1 * V2;

%!error <Too many common indices>
%! ## Testing reduce product with two 2D matrices of identical indices ##
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [5, 3]);
%! M2 = MultiDimVar({"A", "B"}, [5, 3]);
% ACTION
%! M1 * M2;

%!error <Nonconformant arguments>
%! ## Testing reduce product with two 2D matrices of wrong sizes ##
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [5, 3]);
%! M2 = MultiDimVar({"B", "C"}, [5, 3]);
% ACTION
%! M1 * M2;

%!xtest <## Testing reduceproduct with two vectors ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [3], [1; 2; 3]);
%! V2 = MultiDimVar({"A"}, [3], [1; 2; 3]);
%! expected_output = MultiDimVar({}, [1], [14]);
% ACTION
%! test_output = V1 * V2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with a vector and a 2D matrix (index pos1)##>
% SETUP
%! V = MultiDimVar({"A"}, [3], [1; 2; 3]);
%! M = MultiDimVar({"A", "B"}, [3, 2], [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({"B"}, [2], [22; 28]);
% ACTION
%! test_output = V * M;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with a vector and a 2D matrix (index pos2)##>
% SETUP
%! V = MultiDimVar({"A"}, [3], [1; 2; 3]);
%! M = MultiDimVar({"B", "A"}, [2, 3], [1 3 5; 2 4 6]);
%! expected_output = MultiDimVar({"B"}, [2], [22; 28]);
% ACTION
%! test_output = V * M;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with two 2D matrix (pos1)##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [2, 3], [1 2 3; 4 5 6]);
%! M2 = MultiDimVar({"B", "C"}, [3, 4], [1 2 3 4; 5 6 7 8; 9 10 11 12]);
%! expected_output = MultiDimVar({"A", "C"}, [2, 4], [38 44 50 56; 83 98 113 128]);
% ACTION
%! test_output = M1 * M2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with two 2D matrix (pos2)##>
% SETUP
%! M1 = MultiDimVar({"B", "A"}, [3, 2], [1 4; 2 5; 3 6]);
%! M2 = MultiDimVar({"B", "C"}, [3, 4], [1 2 3 4; 5 6 7 8; 9 10 11 12]);
%! expected_output = MultiDimVar({"A", "C"}, [2, 4], [38 44 50 56; 83 98 113 128]);
% ACTION
%! test_output = M1 * M2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with two 2D matrix (pos3)##>
% SETUP
%! M1 = MultiDimVar({"B", "A"}, [3, 2], [1 4; 2 5; 3 6]);
%! M2 = MultiDimVar({"C", "B"}, [4, 3], [1 5 9; 2 6 10; 3 7 11; 4 8 12]);
%! expected_output = MultiDimVar({"A", "C"}, [2, 4], [38 44 50 56; 83 98 113 128]);
% ACTION
%! test_output = M1 * M2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reduceproduct with two 2D matrix (pos4)##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [2, 3], [1 2 3; 4 5 6]);
%! M2 = MultiDimVar({"C", "B"}, [4, 3], [1 5 9; 2 6 10; 3 7 11; 4 8 12]);
%! expected_output = MultiDimVar({"A", "C"}, [2, 4], [38 44 50 56; 83 98 113 128]);
% ACTION
%! test_output = M1 * M2;
% ASSERT
%! assert(isequal(test_output,expected_output))