%!shared indexOrder
%! indexOrder = {"A", "B", "C", "D"};

%!error <Inputs must be of type MultiDimVar or a scalar>
%! ## Testing einsum with one operand of wrong type ##
% SETUP
%! S = [20 2];
%! M = MultiDimVar({"A"}, [5], indexOrder);
% ACTION
%! einsum(S, M);

%!error <Inputs must be of type MultiDimVar or a scalar>
%! ## Testing einsum with one operand of wrong type ##
% SETUP
%! S = [20 2];
%! M = MultiDimVar({"A"}, [5], indexOrder);
% ACTION
%! einsum(M, S);

%!error <Reduce indices not in op1>
%! ## Testing einsum with missing indices (scalar) ##
% SETUP
%! S = 4;
%! M = MultiDimVar({"A", "B"}, [5 2], indexOrder);
% ACTION
%! einsum(S, M, {"B"});

%!error <Reduce indices not in op1>
%! ## Testing einsum with missing indices ##
% SETUP
%! M1 = MultiDimVar({"A"}, [5], indexOrder);
%! M2 = MultiDimVar({"A", "B"}, [5 2], indexOrder);
% ACTION
%! einsum(M1, M2, {"B"});

%!error <Reduce indices not in op2>
%! ## Testing einsum with missing indices ##
% SETUP
%! M1 = MultiDimVar({"A"}, [5], indexOrder);
%! M2 = MultiDimVar({"A", "B"}, [5 2], indexOrder);
% ACTION
%! einsum(M2, M1, {"B"});

%!error <Reduce dimension mismatch>
%! ## Testing einsum with mismatched dimensions ##
% SETUP
%! M1 = MultiDimVar({"B", "C"}, [2 3], indexOrder);
%! M2 = MultiDimVar({"A", "B", "C"}, [3 3 2], indexOrder);
% ACTION
%! einsum(M1, M2, {"C"});

%!error <Page dimension mismatch>
%! ## Testing einsum with mismatched dimensions ##
% SETUP
%! M1 = MultiDimVar({"B", "D"}, [2 3], indexOrder);
%! M2 = MultiDimVar({"A", "B", "C"}, [3 3 3], indexOrder);
% ACTION
%! einsum(M1, M2);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Without contraction%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%!xtest <## Testing einsum with two scalars ##>
% SETUP
%! S1 = 3;
%! S2 = MultiDimVar({}, [1], indexOrder, [4]);
%! expected_output = MultiDimVar({}, [1], indexOrder, [12]);
% ACTION
%! test_output = einsum(S1, S2);
% ASSERT
%! assert(isequal(test_output.indexLabels, expected_output.indexLabels))
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing einsum with one scalar and one vector ##>
% SETUP
%! S = 3;
%! V = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! expected_output = MultiDimVar({"A"}, [3], indexOrder, [3; 6; 9]);
% ACTION
%! test_output = einsum(S, V);
% ASSERT
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing einsum with one scalar and one matrix ##>
% SETUP
%! S = 3;
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2 3; 4 5 6]);
%! expected_output = MultiDimVar({"A", "B"}, [3, 2], indexOrder, ...
%!                               [3 6 9; 12 15 18]);
% ACTION
%! test_output = einsum(S, M);
% ASSERT
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing einsum with two vectors same indices##>
% SETUP
%! V1 = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! V2 = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! expected_output = MultiDimVar({"A"}, [4], indexOrder, [1; 4; 9; 16]);
% ACTION
%! test_output = einsum(V1, V2);
% ASSERT
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing einsum with two vectors different indices##>
% SETUP
%! V1 = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3; 4]);
%! V2 = MultiDimVar({"B"}, [4], indexOrder, [1; 2; 3; 4]);
%! exp_value = [1 2 3 4;2 4 6 8;3 6 9 12;4 8 12 16];
%! expected_output = MultiDimVar({"A", "B"}, [4], indexOrder, exp_value);
% ACTION
%! test_output = einsum(V1, V2);
% ASSERT
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing einsum with a vector and a 2D matrix (common index) ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! M1 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! exp_value = [1 2; 6 8; 15 18];
%! expected_output = MultiDimVar({"A", "B"}, [3, 2], indexOrder, exp_value);
% ACTION
%! test_output = einsum(V1, M1);
% ASSERT
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing einsum with a vector and a 2D matrix (different index) ##>
% SETUP
%! V1 = MultiDimVar({"C"}, [3], indexOrder, [1; 2; 3]);
%! M1 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! exp_value = cat(3, [1 2; 3 4; 5 6], [2 4; 6 8; 10 12], [3 6; 9 12; 15 18]);
%! expected_output = MultiDimVar({"A", "B", "C"}, [], indexOrder, exp_value);
% ACTION
%! test_output = einsum(V1,M1);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing einsum with a vector and a 2D matrix (different index) ##>
% SETUP
%! V1 = MultiDimVar({"B"}, [3], indexOrder, [1; 2; 3]);
%! M1 = MultiDimVar({"A", "C"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! exp_value = cat(3, [1 2 3; 3 6 9; 5 10 15], [2 4 6; 4 8 12; 6 12 18]);
%! expected_output = MultiDimVar({"A", "B", "C"}, [], indexOrder, exp_value);
% ACTION
%! test_output = einsum(V1, M1);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing times with two 2D matrices (same indices) ##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2 3; 4 5 6]);
%! M2 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2 3; 4 5 6]);
%! expected_output = MultiDimVar({"A", "B"}, [3, 2], indexOrder, ...
%!                               [1 4 9; 16 25 36]);
% ACTION
%! test_output = einsum(M1, M2);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing einsum with a 2D and a 3D matrix (same indices) ##>
% SETUP
%! M1 = MultiDimVar({"A", "C"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! value = cat(3, [1 2 1 2; 3 4 3 4; 5 6 5 6], [1 2 1 2; 3 4 3 4; 5 6 5 6]);
%! M2 = MultiDimVar({"A", "B", "C"}, [3, 4, 2], indexOrder, value);
%! expected_value = cat(3, [1 2 1 2; 9 12 9 12; 25 30 25 30], ....
%!                      [2 4 2 4; 12 16 12 16; 30 36 30 36]);
%! expected_output =  MultiDimVar({"A", "B", "C"}, [3, 4, 2], indexOrder, ...
%!                                expected_value);
% ACTION
%! test_output = einsum(M1, M2);
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing einsum with a 2D and a 3D matrix (one different index) ##>
% SETUP
%! M1 = MultiDimVar({"A", "D"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! value = cat(3, [1 2 1 2; 3 4 3 4; 5 6 5 6], [1 2 1 2; 3 4 3 4; 5 6 5 6]);
%! M2 = MultiDimVar({"A", "B", "C"}, [3, 4, 2], indexOrder, value);
%! exp_value = cat(4, ...
%!     cat(3, [1 2 1 2; 9 12 9 12; 25 30 25 30], ...
%!     [1 2 1 2; 9 12 9 12; 25 30 25 30]), ...
%!     cat(3, [2 4 2 4; 12 16 12 16; 30 36 30 36], ...
%!     [2 4 2 4; 12 16 12 16; 30 36 30 36]));
%! expected_output =  MultiDimVar({"A","B","C","D"}, [3,4,2,2], indexOrder, ...
%! exp_value);
% ACTION
%! test_output = einsum(M1, M2);
% ASSERT
%! assert(isequal(test_output,expected_output))

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% With contraction %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%!xtest <## Testing einsum contraction: two vectors ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! V2 = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! expected_output = MultiDimVar({}, [1], indexOrder, [14]);
% ACTION
%! test_output = einsum(V1, V2, {"A"});
% ASSERT
%! assert(isequal(test_output,expected_output),
%! "Expected: %s\nOutput: %s", mat2str(expected_output), mat2str(test_output))

%!xtest <## Testing einsum contraction: vector and 2D matrix (index pos1) ##>
% SETUP
%! V = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! M = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! expected_output = MultiDimVar({"B"}, [2], indexOrder, [22; 28]);
% ACTION
%! test_output = einsum(V, M, {"A"});
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing einsum contraction: vector and 2D matrix (index pos2) ##>
% SETUP
%! V = MultiDimVar({"B"}, [3], indexOrder, [1; 2; 3]);
%! M = MultiDimVar({"A", "B"}, [2, 3], indexOrder, [1 3 5; 2 4 6]);
%! expected_output = MultiDimVar({"A"}, [2], indexOrder, [22; 28]);
% ACTION
%! test_output = einsum(V, M, {"B"});
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing einsum contraction: two 2D matrix (case 1) ##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [3, 2], indexOrder, [1 2; 3 4; 5 6]);
%! M2 = MultiDimVar({"A", "C"}, [3, 4], indexOrder, ...
%!                  [1 2 3 4; 5 6 7 8; 9 10 11 12]);
%! expected_output = MultiDimVar({"B", "C"}, [2, 4], indexOrder, ...
%!                               [61 70 79 88; 76 88 100 112]);
% ACTION
%! test_output = einsum(M1, M2, {"A"});
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing einsum contraction: two 2D matrix (case 2) ##>
% SETUP
%! M1 = MultiDimVar({"A", "C"}, [2, 3], indexOrder, [1 3 5; 2 4 6]);
%! M2 = MultiDimVar({"B", "C"}, [4, 3], indexOrder, ...
%!                  [1 5 9; 2 6 10; 3 7 11; 4 8 12]);
%! expected_output = MultiDimVar({"A", "B"}, [2, 4], indexOrder, ...
%!                               [61 70 79 88; 76 88 100 112]);
% ACTION
%! test_output = einsum(M1, M2, {"C"});
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing einsum contraction: two 2D matrix (case 3) ##>
% SETUP
%! M1 = MultiDimVar({"B", "C"}, [3, 2], indexOrder, [1 4; 2 5; 3 6]);
%! M2 = MultiDimVar({"A", "B"}, [4, 3], indexOrder, ...
%!                  [1 5 9; 2 6 10; 3 7 11; 4 8 12]);
%! expected_output = MultiDimVar({"A", "C"}, [4, 2], indexOrder, ...
%!                               [38 83; 44 98; 50 113; 56 128]);
% ACTION
%! test_output = einsum(M1, M2, {"B"});
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing einsum contraction: two 2D matrix (case 4) ##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [2, 3], indexOrder, [1 3 5; 2 4 6]);
%! M2 = MultiDimVar({"B", "C"}, [3, 4], indexOrder, ... 
%!                  [1 4 7 10; 2 5 8 11; 3 6 9 12]);
%! expected_output = MultiDimVar({"A", "C"}, [2, 4], indexOrder, ...
%!                               [22 49 76 103; 28 64 100 136]);
% ACTION
%! test_output = einsum(M1, M2, {"B"});
% ASSERT
%! assert(isequal(test_output,expected_output))

%!xtest <## Testing einsum contraction: 2D and 3D matrix (with page) ##>
% SETUP
%! M1 = MultiDimVar({"A", "B"}, [2, 3], indexOrder, [1 3 5; 2 4 6]);
%! M2value = cat(3, [1 2 3; 1 5 9], [4 5 6; 2 6 10], ...
%! [7 8 9; 3 7 11], [10 11 12; 4 8 12]);
%! M2 = MultiDimVar({"A", "B", "C"}, [2, 3, 4], indexOrder, M2value);
%! expected_output = MultiDimVar({"A", "C"}, [2, 4], indexOrder, ...
%!                               [22 49 76 103; 76 88 100 112]);
% ACTION
%! test_output = einsum(M1, M2, {"B"});
% ASSERT
%! assert(isequal(test_output,expected_output))