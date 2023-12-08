%!xtest <## Testing times with two scalars ##>
% SETUP
%! S1 = 3;
%! S2 = MultiDimVar({}, [1], [4]);
%! expected_output = MultiDimVar({}, [1], [12]);
% ACTION
%! test_output = S1 .* S2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing times with one scalar and one vector ##>
% SETUP
%! S1 = 3;
%! S2 = MultiDimVar({"A"}, [3], [1; 2; 3]);
%! expected_output = MultiDimVar({"A"}, [3], [3; 6; 9]);
% ACTION
%! test_output = S1 .* S2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing times with one scalar and one matrix ##>
% SETUP
%! S2 = 3;
%! S1 = MultiDimVar({"A", "B"}, [3, 2], [1 2 3; 4 5 6]);
%! expected_output = MultiDimVar({"A", "B"}, [3, 2], [3 6 9; 12 15 18]);
% ACTION
%! test_output = S1 .* S2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!error <Nonconformant arguments>
%! ## Testing times with vectors of equal indexLabels and different sizes ##
% SETUP
%! V1 = MultiDimVar({"A"}, [3]);
%! V2 = MultiDimVar({"A"}, [4]);
% ACTION
%! V1 .* V2

%!xtest <## Testing times with two vectors ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [4], [1; 2; 3; 4]);
%! V2 = MultiDimVar({"A"}, [4], [1; 2; 3; 4]);
%! expected_output = MultiDimVar({"A"}, [4], [1; 4; 9; 16]);
% ACTION
%! test_output = V1 .* V2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing times with two 2D matrices ##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [3, 2], [1 2 3; 4 5 6]);
%! M2 = MultiDimVar({"A", "B"}, [3, 2], [1 2 3; 4 5 6]);
%! expected_output = MultiDimVar({"A", "B"}, [3, 2], [1 4 9; 16 25 36]);
% ACTION
%! test_output = M1 .* M2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!error <not found in second argument>
%! ## Testing times with a vector and a matrix with different indexLabels ##
% SETUP
%! V = MultiDimVar({"A"}, [5]);
%! M = MultiDimVar({"B","C"}, [5, 2]);
% ACTION
%! V .* M

%!error <Nonconformant arguments>
%! ## Testing times with a vector and a matrix with mismatched sizes ##
% SETUP
%! V = MultiDimVar({"A"}, [5]);
%! M = MultiDimVar({"B","A"}, [4, 2]);
% ACTION
%! V .* M

%!xtest <## Testing times with a vector and a 2D matrix (ideal order) ##>
% SETUP
%! V = MultiDimVar({"A"}, [3], [1; 2; 3]);
%! M = MultiDimVar({"A","B"}, [3, 2], [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({"A","B"}, [3, 2], [1 2; 6 8; 15 18]);
% ACTION
%! test_output = V .* M;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing times with a vector and a 2D matrix (opposite order) ##>
% SETUP
%! V = MultiDimVar({"A"}, [3], [1; 2; 3]);
%! M = MultiDimVar({"B","A"}, [2, 3], [1 2 3; 4 5 6]);
%! expected_output = MultiDimVar({"B","A"}, [3, 2], [1 4 9; 4 10 18]);
% ACTION
%! test_output = V .* M;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing times with a 2D and a 3D matrix ##>
% SETUP
%! M1 = MultiDimVar({"A", "C"}, [3, 2], [1 2; 3 4; 5 6]);
%! value = cat(3, [1 2 1 2; 3 4 3 4; 5 6 5 6], [1 2 1 2; 3 4 3 4; 5 6 5 6]);
%! M2 = MultiDimVar({"A", "B", "C"}, [3, 4, 2], value);
%! expected_value = cat(3, [1 2 1 2; 9 12 9 12; 25 30 25 30], [2 4 2 4; 12 16 12 16; 30 36 30 36]);
%! expected_output =  MultiDimVar({"A", "B", "C"}, [3, 4, 2], expected_value);
% ACTION
%! test_output = M1 .* M2;
% ASSERT
%! assert(isequal(test_output,expected_output))




