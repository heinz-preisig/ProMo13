%!shared indexOrder
%! indexOrder = {"A", "B"};

%!test
%! ## Testing sign for an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], indexOrder, [7]);
%! expected_output =  MultiDimVar({}, [1], indexOrder, [1]);
% ACTION
%! test_output = sign(S);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing sign for a vector ##
% SETUP
%! V = MultiDimVar({"A"}, [4], indexOrder, [1;-2;0;4]);
%! expected_output = MultiDimVar({"A"}, [4], indexOrder, [1; -1; 0; 1]);
% ACTION
%! test_output = sign(V);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing sign for a matrix ##
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 0; 3 -4; -5 6]);
%! expected_output = MultiDimVar({"A", "B"}, [3, 2], indexOrder, ...
%!                               [1 0; 1 -1; -1 1]);
% ACTION
%! test_output = sign(M);
% ASSERT
%! assert(isequal(test_output,expected_output))