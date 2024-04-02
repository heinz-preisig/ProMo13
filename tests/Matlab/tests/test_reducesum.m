%!shared indexOrder
%! indexOrder = {"A", "B"};

%!error <Reduce indices not in op1>
%! ## Testing reducesum for an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], indexOrder, [45]);
% ACTION
%! reducesum(S, "A");

%!error <Reduce indices not in op1>
%! ## Testing reducesum for a vector with wrong index set ##
% SETUP
%! V = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
% ACTION
%! reducesum(V, "B");

%!error <Reduce indices not in op1>
%! ## Testing reducesum for a 2D matrix with wrong index set ##
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
% ACTION
%! reducesum(M, "C");

%!xtest <## Testing reducesum for a vector ##>
% SETUP
%! V = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! expected_output = MultiDimVar({}, [1], indexOrder, [10]);
% ACTION
%! test_output = reducesum(V, "A");
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reducesum for a 2D matrix (1st dimension) ##>
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({"B"}, [2, 1], indexOrder, [9; 12]);
% ACTION
%! test_output = reducesum(M, "A");
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reducesum for a 2D matrix (2nd dimension) ##>
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({"A"}, [3 1], indexOrder, [3; 7; 11]);
% ACTION
%! test_output = reducesum(M, "B");
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reducesum for a 3D matrix (2nd dimension) ##>
% SETUP
%! value = cat(3, [1 2; 3 4; 5 6], [1 2; 3 4; 5 6]);
%! M = MultiDimVar({"A", "B", "C"}, [3, 2, 2], indexOrder, value);
%! expected_output =  MultiDimVar({"A", "C"}, [3, 2], indexOrder, ...
%!                                [3 3; 7 7; 11 11]);
% ACTION
%! test_output = reducesum(M, "B");
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing reducesum for a 2D matrix (both dimensions) ##>
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({}, [1], indexOrder, [21]);
% ACTION
%! test_output = reducesum(M, {"A", "B"});
% ASSERT
%! assert(isequal(test_output,expected_output), ...
%!   "Expected %s,\nObtained %s", ...
%!   mat2str(expected_output.value), mat2str(test_output.value))

%!xtest <## Testing reducesum for a 3D matrix (2 dimensions) ##>
% SETUP
%! value = cat(3, [1 2; 3 4; 5 6], [1 2; 3 4; 5 6]);
%! M = MultiDimVar({"A", "B", "C"}, [], indexOrder, value);
%! expected_output = MultiDimVar({"B"}, [2], indexOrder, [18 24]);
% ACTION
%! test_output = reducesum(M, {"A", "C"});
% ASSERT
%! assert(isequal(test_output,expected_output), ...
%!   "Expected %s,\nObtained %s", ...
%!   mat2str(expected_output.value), mat2str(test_output.value))
