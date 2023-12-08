%!test
%! ## Testing size in a vector ##
% SETUP
%! V = MultiDimVar(["A"], [5]);
%! expected_output = [5, 1];
% ACTION
%! test_output = size(V);
% ASSERT
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing size in a 2D matrix ##
% SETUP
%! M = MultiDimVar(["A"], [2,3]);
%! expected_output = [2, 3];
% ACTION
%! test_output = size(M);
% ASSERT
%! assert(isequal(test_output, expected_output))


