%!shared indexOrder
%! indexOrder = {"A", "B"};

%!error <is not an indexSet in>
%! ## Testing product for an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], indexOrder, [45]);
% ACTION
%! product(S, "A");

%!error <is not an indexSet in>
%! ## Testing product for a vector with wrong index set ##
% SETUP
%! V = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
% ACTION
%! product(V, "B");

%!xtest <## Testing product for a vector ##>
% SETUP
%! V = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! expected_output = MultiDimVar({}, [1], indexOrder, [24]);
% ACTION
%! test_output = product(V, "A");
% ASSERT
%! assert(isequal(test_output,expected_output))

%!error <is not an indexSet in>
%! ## Testing product for a 2D matrix with wrong index set ##
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
% ACTION
%! product(M, "C");

%!xtest <## Testing product for a 2D matrix (1st dimension) ##>
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({"B"}, [2, 1], indexOrder, [15; 48]);
% ACTION
%! test_output = product(M, "A");
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing product for a 2D matrix (2nd dimension) ##>
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({"A"}, [3 1], indexOrder, [2; 12; 30]);
% ACTION
%! test_output = product(M, "B");
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing product for a 3D matrix (2nd dimension) ##>
% SETUP
%! value = cat(3, [1 2; 3 4; 5 6], [1 2; 3 4; 5 6]);
%! M = MultiDimVar({"A", "B", "C"}, [3, 2, 2], indexOrder, value);
%! expected_output =  MultiDimVar({"A", "C"}, [3, 2], indexOrder, ...
%!                                [2 2; 12 12; 30 30]);
% ACTION
%! test_output = product(M, "B");
% ASSERT
%! assert(isequal(test_output,expected_output))
