%!test
%! ## Testing abs for an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], [-23]);
%! expected_output = MultiDimVar({}, [1], [23]);;
% ACTION
%! test_output = abs(S);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing abs for a vector ##
% SETUP
%! V = MultiDimVar({"A"}, [3], [-23; 0; 7]);
%! expected_output = MultiDimVar({"A"}, [3], [23; 0; 7]);
% ACTION
%! test_output = abs(V);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing abs for a matrix ##
% SETUP
%! M = MultiDimVar({"A", "B"}, [2,3], [-23 0 7; 2 -5 -10]);
%! expected_output = MultiDimVar({"A", "B"}, [2,3], [23 0 7; 2 5 10]);
% ACTION
%! test_output = abs(M);
% ASSERT
%! assert(isequal(test_output,expected_output))