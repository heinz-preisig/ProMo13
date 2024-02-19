%!shared indexOrder
%! indexOrder = {"A", "B", "C", "D"};

%!error <Inputs must be of type MultiDimVar or a scalar>
%! ## Testing times with one operand of wrong type ##
% SETUP
%! S = [20 2];
%! M = MultiDimVar({"A"}, [5], indexOrder);
% ACTION
%! S .* M;

%!error <nonconformant arguments>
%! ## Testing times with vectors of equal indexLabels and different sizes ##
% SETUP
%! V1 = MultiDimVar({"A"}, [3], indexOrder);
%! V2 = MultiDimVar({"A"}, [4], indexOrder);
% ACTION
%! V1 .* V2

%!error <nonconformant arguments>
%! ## Testing times with a vector and a matrix with mismatched sizes ##
% SETUP
%! V = MultiDimVar({"A"}, [5], indexOrder);
%! M = MultiDimVar({"B","A"}, [4, 2], indexOrder);
% ACTION
%! V .* M

%!xtest <## Testing times with two scalars ##>
% SETUP
%! S1 = 3;
%! S2 = MultiDimVar({}, [1], indexOrder, [4]);
%! expected_output = MultiDimVar({}, [1], indexOrder, [12]);
% ACTION
%! test_output = S1 .* S2;
% ASSERT
%! assert(isequal(test_output.indexLabels, expected_output.indexLabels))
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing times with one scalar and one vector ##>
% SETUP
%! S1 = 3;
%! S2 = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! expected_output = MultiDimVar({"A"}, [3], indexOrder, [3; 6; 9]);
% ACTION
%! test_output = S1 .* S2;
% ASSERT
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing times with one scalar and one matrix ##>
% SETUP
%! S2 = 3;
%! S1 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2 3; 4 5 6]);
%! expected_output = MultiDimVar({"A", "B"}, [3, 2], indexOrder, ...
%!                               [3 6 9; 12 15 18]);
% ACTION
%! test_output = S1 .* S2;
% ASSERT
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing times with two vectors same indices##>
% SETUP
%! V1 = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! V2 = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! expected_output = MultiDimVar({"A"}, [4], indexOrder, [1; 4; 9; 16]);
% ACTION
%! test_output = V1 .* V2;
% ASSERT
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing times with two vectors different indices##>
% SETUP
%! V1 = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! V2 = MultiDimVar({"B"}, [4], indexOrder, [1; 2; 3; 4]);
%! exp_value = [1 2 3 4;2 4 6 8;3 6 9 12;4 8 12 16];
%! expected_output = MultiDimVar({"A", "B"}, [4], indexOrder, exp_value);
% ACTION
%! test_output = V1 .* V2;
% ASSERT
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing times with a vector and a 2D matrix with common index ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! M1 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! exp_value = [1 2; 6 8; 15 18];
%! expected_output = MultiDimVar({"A", "B"}, [3, 2], indexOrder, exp_value);
% ACTION
%! test_output = V1 .* M1;
% ASSERT
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing times with a vector and a 2D matrix with common index) ##>
% SETUP
%! V = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! M = MultiDimVar({"B","A"}, [2, 3], indexOrder, [1 2 3; 4 5 6]);
%! expected_output = MultiDimVar({"B","A"}, [3, 2], indexOrder, ...
%!                               [1 4 9; 4 10 18]);
% ACTION
%! test_output = V .* M;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing times with a vector and a 2D matrix with different index ##>
% SETUP
%! V1 = MultiDimVar({"C"}, [3], indexOrder, [1; 2; 3]);
%! M1 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! exp_value = cat(3, [1 2; 3 4; 5 6], [2 4; 6 8; 10 12], [3 6; 9 12; 15 18]);
%! expected_output = MultiDimVar({"A", "B", "C"}, [], indexOrder, exp_value);
% ACTION
%! test_output = V1 .* M1;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing times with a vector and a 2D matrix with different index ##>
% SETUP
%! V1 = MultiDimVar({"B"}, [3], indexOrder, [1; 2; 3]);
%! M1 = MultiDimVar({"A", "C"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! exp_value = cat(3, [1 2 3; 3 6 9; 5 10 15], [2 4 6; 4 8 12; 6 12 18]);
%! expected_output = MultiDimVar({"A", "B", "C"}, [], indexOrder, exp_value);
% ACTION
%! test_output = V1 .* M1;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing times with two 2D matrices ##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2 3; 4 5 6]);
%! M2 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2 3; 4 5 6]);
%! expected_output = MultiDimVar({"A", "B"}, [3, 2], indexOrder, ...
%!                               [1 4 9; 16 25 36]);
% ACTION
%! test_output = M1 .* M2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing times with a 2D and a 3D matrix ##>
% SETUP
%! M1 = MultiDimVar({"A", "C"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! value = cat(3, [1 2 1 2; 3 4 3 4; 5 6 5 6], [1 2 1 2; 3 4 3 4; 5 6 5 6]);
%! M2 = MultiDimVar({"A", "B", "C"}, [3, 4, 2], indexOrder, value);
%! expected_value = cat(3, [1 2 1 2; 9 12 9 12; 25 30 25 30], ....
%!                      [2 4 2 4; 12 16 12 16; 30 36 30 36]);
%! expected_output =  MultiDimVar({"A", "B", "C"}, [3, 4, 2], indexOrder, ...
%!                                expected_value);
% ACTION
%! test_output = M1 .* M2;
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing times with a 2D and a 3D matrix one different index##>
% SETUP
%! M1 = MultiDimVar({"A", "D"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! value = cat(3, [1 2 1 2; 3 4 3 4; 5 6 5 6], [1 2 1 2; 3 4 3 4; 5 6 5 6]);
%! M2 = MultiDimVar({"A", "B", "C"}, [3, 4, 2], indexOrder, value);
%! exp_value = cat(4, ...
%!     cat(3, [1 2 1 2; 9 12 9 12; 25 30 25 30], ...
%!     [1 2 1 2; 9 12 9 12; 25 30 25 30]), ...
%!     cat(3, [2 4 2 4; 12 16 12 16; 30 36 30 36], ...
%!     [2 4 2 4; 12 16 12 16; 30 36 30 36]));
%! expected_output =  MultiDimVar({"A","B","C","D"}, [3,4,2,2], indexOrder, exp_value);
% ACTION
%! test_output = M1 .* M2;
% ASSERT
%! assert(isequal(test_output,expected_output))