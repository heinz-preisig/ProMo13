%!test
%! ## Testing isvector in an scalar ##
% SETUP
%! S = MultiDimVar(["A"], [1]);
%! expected_output = true;
% ACTION
%! test_output = isvector(S);
% ASSERT
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing isvector in a vector ##
% SETUP
%! V = MultiDimVar(["A"], [3]);
%! expected_output = true;
% ACTION
%! test_output = isvector(V);
% ASSERT
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing isvector in a 2D matrix ##
% SETUP
%! M = MultiDimVar(["A", "B"], [3,5]);
%! expected_output = false;
% ACTION
%! test_output = isvector(M);
% ASSERT
%! assert(isequal(test_output, expected_output))