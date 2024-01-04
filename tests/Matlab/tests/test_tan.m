%!shared indexOrder
%! indexOrder = {"A", "B"};

%!test
%! ## Testing tan for an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], indexOrder, [2]);
%! expected_output = MultiDimVar({}, [1], indexOrder, tan(2));;
% ACTION
%! test_output = tan(S);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing abs for a vector ##
% SETUP
%! V = MultiDimVar({"A"}, [3], indexOrder, [2; 1; 3]);
%! expected_output = MultiDimVar({"A"}, [3], indexOrder, tan([2; 1; 3]));
% ACTION
%! test_output = tan(V);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing abs for a matrix ##
% SETUP
%! M = MultiDimVar({"A", "B"}, [2,3], indexOrder, [2 1 3; 1 2 3]);
%! expected_output = MultiDimVar({"A", "B"}, [2,3], indexOrder, ...
%!                               tan([2 1 3; 1 2 3]));
% ACTION
%! test_output = tan(M);
% ASSERT
%! assert(isequal(test_output,expected_output))