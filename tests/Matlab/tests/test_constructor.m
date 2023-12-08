%!xtest
%! ## Testing the creation of an empty vector ##
% SETUP
%! indexLabels = {"N"};
%! indexSizes = [5];
%! A = MultiDimVar(indexLabels, indexSizes);
%! expected_output = true;
% ACTION
%! test_output = A.value == [0; 0; 0; 0; 0] && ...
%!               isequal(A.indexLabels, indexLabels);
% ASSERT
%! assert(test_output == expected_output);

%!xtest
%! ## Testing the creation of a vector with value ##
% SETUP
%! indexLabels = {"N"};
%! indexSizes = [5];
%! value = [1; 2; 3; 4; 5];
%! A = MultiDimVar(indexLabels, indexSizes, value);
%! expected_output = true;
% ACTION
%! test_output = A.value == value && ...
%!               isequal(A.indexLabels, indexLabels);
% ASSERT
%! assert(test_output == expected_output);

%!xtest
%! ## Testing the creation of an empty 2D matrix ##
% SETUP
%! indexLabels = {"N", "A"};
%! indexSizes = [5, 3];
%! A = MultiDimVar(indexLabels, indexSizes);
%! expected_output = true;
% ACTION
%! test_output = A.value == [0 0 0; 0 0 0; 0 0 0; 0 0 0; 0 0 0] && ...
%!               isequal(A.indexLabels, indexLabels);
% ASSERT
%! assert(test_output == expected_output);

%!xtest
%! ## Testing the creation of a matrix with value ##
% SETUP
%! indexLabels = {"N", "A"};
%! indexSizes = [5, 3];
%! value = [1 2 3; 4 5 6; 7 8 9; 10 11 12; 13 14 15];
%! A = MultiDimVar(indexLabels, indexSizes, value);
%! expected_output = true;
% ACTION
%! test_output = A.value == value && ...
%!               isequal(A.indexLabels, indexLabels);
% ASSERT
%! assert(test_output == expected_output);

