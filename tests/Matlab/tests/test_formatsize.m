%!shared indexOrder
%! indexOrder = {"A", "B"};

%!test
%! ## Testing formatsize for an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], indexOrder);
%! expected_output = "1x1";
% ACTION
%! test_output = formatsize(S);
% ASSERT
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing formatsize for a vector ##
% SETUP
%! V = MultiDimVar({"A"}, [5], indexOrder);
%! expected_output = "5x1";
% ACTION
%! test_output = formatsize(V);
% ASSERT
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing formatsize for a matrix ##
% SETUP
%! M = MultiDimVar({}, [5, 3], indexOrder);
%! expected_output = "5x3";
% ACTION
%! test_output = formatsize(M);
% ASSERT
%! assert(isequal(test_output, expected_output))