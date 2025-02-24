%!shared indexOrder
%! indexOrder = {"A", "B"};

%!test
%! ## Testing isvector in an scalar ##
% SETUP
%! S = MultiDimVar(["A"], [1], indexOrder);
%! expected_output = true;
% ACTION
%! test_output = isvector(S);
% ASSERT
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing isvector in a vector ##
% SETUP
%! V = MultiDimVar(["A"], [3], indexOrder);
%! expected_output = true;
% ACTION
%! test_output = isvector(V);
% ASSERT
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing isvector in a 2D matrix ##
% SETUP
%! M = MultiDimVar(["A", "B"], [3,5], indexOrder);
%! expected_output = false;
% ACTION
%! test_output = isvector(M);
% ASSERT
%! assert(isequal(test_output, expected_output))