%!error <Both operands need to be of type MultiDimVar>
%! ## Testing power with operands of the wrong type ##
% SETUP
%! S = 20;
%! V = MultiDimVar({"A"}, [5]);
% ACTION
%! S .^ V;

%!error <IndexLabels do not match>
%! ## Testing power for vectors with mismatching indexLabel ##
% SETUP
%! V1 = MultiDimVar({"A"}, [4], [1; 2; 3; 4]);
%! V2 = MultiDimVar({"B"}, [4], [1; 2; 3; 4]);
% ACTION
%! V1 .^ V2;

%!error <Nonconformant arguments>
%! ## Testing power for vectors with different sizes ##
% SETUP
%! V1 = MultiDimVar({"A"}, [4], [1; 2; 3; 4]);
%! V2 = MultiDimVar({"A"}, [3], [1; 2; 3]);
% ACTION
%! V1 .^ V2;

%!xtest <## Testing power for two vectors ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [3], [1; 2; 3]);
%! V2 = MultiDimVar({"A"}, [3], [1; 2; 3]);
%! expected_output = MultiDimVar({"A"}, [3], [1; 4; 27]);
% ACTION
%! test_output = V1 .^ V2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing power for two 2D matrices ##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [2, 3], [1 2 3; 4 5 6]);
%! M2 = MultiDimVar({"A", "B"}, [2, 3], [3 2 1; 0 2 1]);
%! expected_output = MultiDimVar({"A", "B"}, [2, 3], [1 4 3; 1 25 6]);
% ACTION
%! test_output = M1 .^ M2;
% ASSERT
%! assert(isequal(test_output,expected_output))

