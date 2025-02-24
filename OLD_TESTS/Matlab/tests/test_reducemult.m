%!shared indexOrder
%! indexOrder = {"A", "B"};

%!error <Reduce indices not in op1>
%! ## Testing product for an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], indexOrder, [45]);
% ACTION
%! reducemult(S, "A");

%!error <Reduce indices not in op1>
%! ## Testing product for a vector with wrong index set ##
% SETUP
%! V = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
% ACTION
%! reducemult(V, "B");

%!error <Reduce indices not in op1>
%! ## Testing product for a 2D matrix with wrong index set ##
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
% ACTION
%! reducemult(M, "C");

%!xtest <## Testing product for a vector ##>
% SETUP
%! V = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! expected_output = MultiDimVar({}, [1], indexOrder, [24]);
% ACTION
%! test_output = reducemult(V, "A");
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing product for a 2D matrix (1st dimension) ##>
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({"B"}, [2, 1], indexOrder, [15; 48]);
% ACTION
%! test_output = reducemult(M, "A");
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing product for a 2D matrix (2nd dimension) ##>
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({"A"}, [3 1], indexOrder, [2; 12; 30]);
% ACTION
%! test_output = reducemult(M, "B");
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing product for a 3D matrix (2nd dimension) ##>
% SETUP
%! value = cat(3, [1 2; 3 4; 5 6], [1 2; 3 4; 5 6]);
%! M = MultiDimVar({"A", "B", "C"}, [3, 2, 2], indexOrder, value);
%! expected_output =  MultiDimVar({"A", "C"}, [3, 2], indexOrder, ...
%!                                [2 2; 12 12; 30 30]);
% ACTION
%! test_output = reducemult(M, "B");
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing product for a 2D matrix (both dimensions) ##>
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({}, [1], indexOrder, [720]);
% ACTION
%! test_output = reducemult(M, {"A", "B"});
% ASSERT
%! assert(isequal(test_output,expected_output), ...
%!   "Expected %s,\nObtained %s", ...
%!   mat2str(expected_output.value), mat2str(test_output.value))

%!xtest <## Testing product for a 3D matrix (2 dimensions) ##>
% SETUP
%! value = cat(3, [1 2; 3 4; 5 6], [1 2; 3 4; 5 6]);
%! M = MultiDimVar({"A", "B", "C"}, [], indexOrder, value);
%! expected_output = MultiDimVar({"B"}, [2], indexOrder, [225 2304]);
% ACTION
%! test_output = reducemult(M, {"A", "C"});
% ASSERT
%! assert(isequal(test_output,expected_output), ...
%!   "Expected %s,\nObtained %s", ...
%!   mat2str(expected_output.value), mat2str(test_output.value))
