%!xtest <## Testing sparse for a vector ##>
% SETUP
%! V = MultiDimVar({"A"}, [4], [1; 0; 0; 4]);
%! expected_output = true;
% ACTION
%! test_output = issparse(sparse(V).value);
% ASSERT
%! assert(isequal(test_output, expected_output))

%!xtest <## Testing sparse for a matrix ##>
% SETUP
%! M = MultiDimVar({"A", "B"}, [2 3], [0 0 3; 4 0 0]);
%! expected_output = true;
% ACTION
%! test_output = issparse(sparse(M).value);
% ASSERT
%! assert(isequal(test_output, expected_output))

