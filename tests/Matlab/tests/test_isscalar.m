%!xtest
%! ## Testing isscalar in an scalar ##
% SETUP
%! S = MultiDimVar(["A"], [1]);
%! expected_output = true;
% ACTION
%! test_output = isscalar(S);
% ASSERT
%! assert(isequal(test_output, expected_output))

%!xtest
%! ## Testing isscalar in a vector ##
% SETUP
%! V = MultiDimVar(["A"], [3]);
%! expected_output = false;
% ACTION
%! test_output = isscalar(V);
% ASSERT
%! assert(isequal(test_output, expected_output))