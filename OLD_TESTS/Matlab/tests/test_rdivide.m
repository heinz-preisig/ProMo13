%!shared indexOrder
%! indexOrder = {"A", "B"};

%!error <Nonconformant arguments>
%! ## Testing rdivide with a vector and a matrix ##
% SETUP
%! V = MultiDimVar({"A"}, [4], indexOrder);
%! M = MultiDimVar({"A","B"}, [4, 3], indexOrder);
% ACTION
%! V ./ M

%!error <Nonconformant arguments>
%! ## Testing rdivide with two vectors of diferent size ##
% SETUP
%! V1 = MultiDimVar({"A"}, [4], indexOrder);
%! V2 = MultiDimVar({"A"}, [5], indexOrder);
% ACTION
%! V1 ./ V2

%!error <Nonconformant arguments>
%! ## Testing rdivide with two 2D matrices of diferent size ##
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [4, 3], indexOrder);
%! M2 = MultiDimVar({"A", "B"}, [5, 3], indexOrder);
% ACTION
%! M1 ./ M2

%!xtest <## Testing rdivide with two scalars ##>
% SETUP
%! S1 = 20;
%! S2 = MultiDimVar({}, [1], indexOrder, [10]);
%! expected_output = MultiDimVar({}, [1], indexOrder, [2]);
% ACTION
%! test_output = S1 ./ S2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing rdivide with one scalar and one vector ##>
% SETUP
%! S = 20;
%! V = MultiDimVar({"A"}, [3], indexOrder, [10; 5; 4]);
%! expected_output = MultiDimVar({"A"}, [3], indexOrder, [2; 4; 5]);
% ACTION
%! test_output = S ./ V;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing rdivide with one scalar and one 2D matrix ##>
% SETUP
%! S = MultiDimVar({}, [1], indexOrder, [2]);
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [10 4 6; 0 8 2]);
%! expected_output = MultiDimVar({"A", "B"}, [3, 2], indexOrder, ...
%!                               [5 2 3; 0 4 1]);
% ACTION
%! test_output = M ./ S;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing rdivide with two vectors ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [3], indexOrder, [10; 4; 8]);
%! V2 = MultiDimVar({"A"}, [3], indexOrder, [5; 2; 4]);
%! expected_output = MultiDimVar({"A"}, [3], indexOrder, [2; 2; 2]);
% ACTION
%! test_output = V1 ./ V2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing rdivide with two 2D matrices ##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [10 4 6; 0 8 2]);
%! M2 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [2 2 2; 2 2 2]);
%! expected_output = MultiDimVar({"A", "B"}, [3, 2], indexOrder, ...
%!                               [5 2 3; 0 4 1]);
% ACTION
%! test_output = M1 ./ M2;
% ASSERT
%! assert(isequal(test_output,expected_output))