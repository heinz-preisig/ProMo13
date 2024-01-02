%!test
%! ## Testing ctranspose for an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], [7]);
%! expected_output = MultiDimVar({}, [1], [7]);
% ACTION
%! test_output = S';
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing ctranspose for a vector ##
% SETUP
%! V = MultiDimVar({"A"}, [4], [1;2;3;4]);
%! expected_output = MultiDimVar({"A"}, [4], [1;2;3;4]);
% ACTION
%! test_output = V';
% ASSERT
%! assert(isequal(test_output,expected_output))

%!test
%! ## Testing ctranspose for a matrix ##
% SETUP
%! M = MultiDimVar({"A", "B"}, [3, 2], [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({"B", "A"}, [2, 3], [1 3 5; 2 4 6]);
% ACTION
%! test_output = M';
% ASSERT
%! assert(isequal(test_output,expected_output))