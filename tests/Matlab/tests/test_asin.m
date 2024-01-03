%!shared indexOrder
%! indexOrder = {"A", "B"};

%!test
%! ## Testing asin for an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], indexOrder, [2]);
%! expected_output = MultiDimVar({}, [1], indexOrder, asin(2));;
% ACTION
%! test_output = asin(S);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing abs for a vector ##
% SETUP
%! V = MultiDimVar({"A"}, [3], indexOrder, [2; 1; 3]);
%! expected_output = MultiDimVar({"A"}, [3], indexOrder, asin([2; 1; 3]));
% ACTION
%! test_output = asin(V);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing abs for a matrix ##
% SETUP
%! M = MultiDimVar({"A", "B"}, [2,3], indexOrder, [2 1 3; 1 2 3]);
%! expected_output = MultiDimVar({"A", "B"}, [2,3], indexOrder, ...
%!                               asin([2 1 3; 1 2 3]));
% ACTION
%! test_output = asin(M);
% ASSERT
%! assert(isequal(test_output,expected_output))