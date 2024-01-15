%!shared V, M, indexOrder
%! indexOrder = {"A", "B"};
%! V = MultiDimVar({"A"}, [5], indexOrder, [1; 2; 3; 4; 5]);
%! M = MultiDimVar({"A", "B"}, [5, 3], indexOrder, ...
%!                 [1 2 3;4 5 6;7 8 9;10 11 12;13 14 15]);

%!error <out of bound>
%! ## Testing subsasgn with index out of bounds ##
% ACTION
%! V(8) = 348;

%!test
%! ## Testing subsasgn with scalar on vector ##
% SETUP
%! test_output = V;
%! expected_output = MultiDimVar({"A"}, [5], indexOrder, [1; 348; 3; 4; 5]);
% ACTION
%! test_output(2) = 348;
% ASSERTIONS
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing subsasgn with vector on vector ##
% SETUP
%! test_output = V;
%! expected_output = MultiDimVar({"A"}, [5], indexOrder, [1; 348; 445; 4; 5]);
% ACTION
%! test_output([2 3]) = [348; 445];
% ASSERTIONS
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing subsasgn with scalar on matrix ##
% SETUP
%! test_output = M;
%! expected_output = MultiDimVar({"A", "B"}, [5, 3],  indexOrder, ...
%!                        [1 2 3; 4 348 6; 7 8 9; 10 11 12; 13 14 15]);
% ACTION
%! test_output(2,2) = 348;
% ASSERTIONS
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing subsasgn with row on matrix ##
% SETUP
%! test_output = M;
%! expected_output = MultiDimVar({"A", "B"}, [5, 3], indexOrder, ...
%!                        [1 2 3; 348 35 123; 7 8 9; 10 11 12; 13 14 15]);
% ACTION
%! test_output(2,:) = [348 35 123];
% ASSERTIONS
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing subsasgn with column on matrix ##
% SETUP
%! test_output = M;
%! expected_output = MultiDimVar({"A", "B"}, [5, 3], indexOrder, ...
%!                        [1 1 3; 4 1 6; 7 1 9; 10 1 12; 13 1 15]);
% ACTION
%! test_output(:,2) = [1; 1; 1; 1; 1];
% ASSERTIONS
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing subsasgn with matrix on matrix ##
% SETUP
%! test_output = M;
%! expected_output = MultiDimVar({"A", "B"}, [5, 3], indexOrder, ...
%!                        [1 2 3; 4 1 1; 7 1 1; 10 1 1; 13 14 15]);
% ACTION
%! test_output([2 3 4],[2 3]) = [1 1; 1 1; 1 1];
% ASSERTIONS
%! assert(isequal(test_output, expected_output))