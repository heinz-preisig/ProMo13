%!shared indexOrder
%! indexOrder = {"A", "B", "C", "D"};

%!xtest
%! ## Testing the creation of an empty vector ##
% SETUP
%! indexLabels = {"A"};
%! indexSizes = [5];
%! value = [0; 0; 0; 0; 0];
%! A = MultiDimVar(indexLabels, indexSizes, indexOrder);
%! expected_output = true;
% ACTION
%! test_output = isequal(A.value, value) && isequal(A.indexLabels, indexLabels);
% ASSERT
%! assert(isequal(test_output, expected_output));

%!xtest
%! ## Testing the creation of a vector with value ##
% SETUP
%! indexLabels = {"A"};
%! indexSizes = [5];
%! value = [1; 2; 3; 4; 5];
%! A = MultiDimVar(indexLabels, indexSizes, indexOrder, value);
%! expected_output = true;
% ACTION
%! test_output = isequal(A.value, value) && isequal(A.indexLabels, indexLabels);
% ASSERT
%! assert(isequal(test_output, expected_output));

%!xtest
%! ## Testing the creation of a vector from row vector ##
% SETUP
%! indexLabels = {"A"};
%! indexSizes = [5];
%! value = [1 2 3 4 5];
%! expected_value = [1; 2; 3; 4; 5];
%! A = MultiDimVar(indexLabels, indexSizes, indexOrder, value);
%! expected_output = true;
% ACTION
%! test_output = isequal(A.value, expected_value) && ...
%!   isequal(A.indexLabels, indexLabels);
% ASSERT
%! assert(isequal(test_output, expected_output));

%!xtest
%! ## Testing the creation of a matrix from a row vector ##
% SETUP
%! indexLabels = {"A", "B"};
%! indexSizes = [1, 5];
%! value = [1 2 3 4 5];
%! A = MultiDimVar(indexLabels, indexSizes, indexOrder, value);
%! expected_output = true;
% ACTION
%! test_output = isequal(A.value, value) && isequal(A.indexLabels, indexLabels);
% ASSERT
%! assert(isequal(test_output, expected_output));

%!xtest
%! ## Testing the creation of an empty 2D matrix ##
% SETUP
%! indexLabels = {"A", "B"};
%! indexSizes = [5, 3];
%! value = [0 0 0; 0 0 0; 0 0 0; 0 0 0; 0 0 0];
%! A = MultiDimVar(indexLabels, indexSizes, indexOrder);
%! expected_output = true;
% ACTION
%! test_output = isequal(A.value, value) && isequal(A.indexLabels, indexLabels);
% ASSERT
%! assert(isequal(test_output, expected_output));

%!xtest
%! ## Testing the creation of a matrix with value ##
% SETUP
%! indexLabels = {"A", "B"};
%! indexSizes = [5, 3];
%! value = [1 2 3; 4 5 6; 7 8 9; 10 11 12; 13 14 15];
%! A = MultiDimVar(indexLabels, indexSizes, indexOrder, value);
%! expected_output = true;
% ACTION
%! test_output = isequal(A.value, value) && isequal(A.indexLabels, indexLabels);
% ASSERT
%! assert(isequal(test_output, expected_output));

%!xtest
%! ## Testing the creation of a matrix with wrong index ordering ##
% SETUP
%! indexLabels = {"B", "A"};
%! indexSizes = [5, 3];
%! value = [1 2 3; 4 5 6; 7 8 9; 10 11 12; 13 14 15];
%! A = MultiDimVar(indexLabels, indexSizes, indexOrder, value);
%! expected_output = true;
% ACTION
%! test_output = isequal(A.value, value') && isequal(A.indexLabels, {"A", "B"});
% ASSERT
%! assert(isequal(test_output, expected_output));

%!xtest
%! ## Testing the creation of a matrix with wrong index ordering (skiping some) ##
% SETUP
%! indexLabels = {"D", "B"};
%! indexSizes = [5, 3];
%! value = [1 2 3; 4 5 6; 7 8 9; 10 11 12; 13 14 15];
%! A = MultiDimVar(indexLabels, indexSizes, indexOrder, value);
%! expected_output = true;
% ACTION
%! test_output = isequal(A.value, value') && isequal(A.indexLabels, {"B", "D"});
% ASSERT
%! assert(isequal(test_output, expected_output));

%!xtest
%! ## Testing the creation of a 4D matrix##
% SETUP
%! indexLabels = {"A", "B", "C", "D"};
%! indexSizes = [3, 4, 2, 2];
%! value = cat(4, cat(3, [1 2 1 2; 9 12 9 12; 25 30 25 30], [1 2 1 2; 9 12 9 12; 25 30 25 30]), cat(3, [2 4 2 4; 12 16 12 16; 30 36 30 36], [2 4 2 4; 12 16 12 16; 30 36 30 36]));
%! A = MultiDimVar(indexLabels, indexSizes, indexOrder, value);
%! expected_output = true;
% ACTION
%! test_output = isequal(A.value, value) && isequal(A.indexLabels, indexLabels);
% ASSERT
%! assert(isequal(test_output, expected_output));

