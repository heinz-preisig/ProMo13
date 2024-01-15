%!shared indexOrder
%! indexOrder = {"A", "B"};

%!error <IndexLabels do not match>
%! ## Testing plus for vectors with mismatching indexLabel ##
% SETUP
%! V1 = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! V2 = MultiDimVar({"B"}, [4], indexOrder, [1; 2; 3; 4]);
% ACTION
%! V1 + V2;

%!error <Nonconformant arguments>
%! ## Testing plus for vectors with different sizes ##
% SETUP
%! V1 = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! V2 = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
% ACTION
%! V1 + V2;

%!xtest <## Testing plus for vectors ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! V2 = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! expected_output = MultiDimVar({"A"}, [4], indexOrder, [2; 4; 6; 8]);
% ACTION
%! test_output = V1 + V2;
% ASSERT
%! assert(isequal(test_output, expected_output))

%!xtest <## Testing plus for 2D matrices ##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [2, 3], indexOrder, [1 2 3; 4 5 6]);
%! M2 = MultiDimVar({"A", "B"}, [2, 3], indexOrder, [1 2 3; 4 5 6]);
%! expected_output = MultiDimVar({"A", "B"}, [2, 3], indexOrder, ...
%!                               [2 4 6; 8 10 12]);
% ACTION
%! test_output = M1 + M2;
% ASSERT
%! assert(isequal(test_output,expected_output))



