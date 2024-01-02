%!shared V, M
%! V = MultiDimVar({"A"}, [5], [1; 2; 3; 4; 5]);
%! M = MultiDimVar({"A", "B"}, [5, 3], [1 2 3;4 5 6;7 8 9;10 11 12;13 14 15]);

%!error <out of bound>
%! ## Testing out of bounds in a vector ##
% ACTION
%! test_output = V(7);

%!test
%! ## Testing subsref in a vector (simple index) ##
% SETUP
%! expected_output = MultiDimVar({"A"}, [1], [2]);
% ACTION
%! test_output = V(2);
% ASSERTIONS
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing subsref in a vector (slice) ##
% SETUP
%! expected_output = MultiDimVar({"A"}, [2], [2; 3]);
% ACTION
%! test_output = V([2 3]);
% ASSERTIONS
%! assert(isequal(test_output, expected_output))

%!error <out of bound>
%! ## Testing out of bounds in a matrix ##
% ACTION
%! test_output = M(7, 2);

%!test
%! ## Testing subsref in a 2D matrix (simple index 2D) ##
% SETUP
%! expected_output = MultiDimVar({"A", "B"}, [1, 1], [6]);
% ACTION
%! test_output = M(2,3);
% ASSERTIONS
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing subsref in a 2D matrix (number slice) ##
% SETUP
%! expected_output = MultiDimVar({"A", "B"}, [2, 2], [4 6; 7 9]);
% ACTION
%! test_output = M([2 3],[1 3]);
% ASSERTIONS
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing subsref in a 2D matrix (horizontal : slice) ##
% SETUP
%! expected_output = MultiDimVar({"A", "B"}, [2, 3], [4 5 6; 7 8 9]);
% ACTION
%! test_output = M([2 3],:);
% ASSERTIONS
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing subsref in a 2D matrix (vertical : slice) ##
% SETUP
%! expected_output = MultiDimVar({"A", "B"}, [5, 1], [2;5;8;11;14]);
% ACTION
%! test_output = M(:,2);
% ASSERTIONS
%! assert(isequal(test_output, expected_output))
