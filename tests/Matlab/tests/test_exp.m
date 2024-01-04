%!shared indexOrder
%! indexOrder = {"A", "B"};

%!test
%! ## Testing exp for an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], indexOrder, [2]);
%! expected_output = MultiDimVar({}, [1], indexOrder, exp(2));;
% ACTION
%! test_output = exp(S);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing abs for a vector ##
% SETUP
%! V = MultiDimVar({"A"}, [3], indexOrder, [-2; 0; 3]);
%! expected_output = MultiDimVar({"A"}, [3], indexOrder, exp([-2; 0; 3]));
% ACTION
%! test_output = exp(V);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing abs for a matrix ##
% SETUP
%! M = MultiDimVar({"A", "B"}, [2,3], indexOrder, [-2 0 3; 1 2 -3]);
%! expected_output = MultiDimVar({"A", "B"}, [2,3], indexOrder, ...
%!                               exp([-2 0 3; 1 2 -3]));
% ACTION
%! test_output = exp(M);
% ASSERT
%! assert(isequal(test_output,expected_output))