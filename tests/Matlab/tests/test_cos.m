%!test
%! ## Testing cos for an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], [2]);
%! expected_output = MultiDimVar({}, [1], cos(2));;
% ACTION
%! test_output = cos(S);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing abs for a vector ##
% SETUP
%! V = MultiDimVar({"A"}, [3], [2; 1; 3]);
%! expected_output = MultiDimVar({"A"}, [3], cos([2; 1; 3]));
% ACTION
%! test_output = cos(V);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing abs for a matrix ##
% SETUP
%! M = MultiDimVar({"A", "B"}, [2,3], [2 1 3; 1 2 3]);
%! expected_output = MultiDimVar({"A", "B"}, [2,3], cos([2 1 3; 1 2 3]));
% ACTION
%! test_output = cos(M);
% ASSERT
%! assert(isequal(test_output,expected_output))