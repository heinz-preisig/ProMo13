%!shared indexOrder
%! indexOrder = {"A", "B"};

%!test
%! ## Testing disp of an scalar ##
% SETUP
%! S = MultiDimVar({}, [1], indexOrder, 385);
%! expected_output = ["Indices: None\n", ...
%!                    "385\n"];
% ACTION
%! test_output = evalc('disp(S)');
% ASSERT
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing disp of an empty vector ##
% SETUP
%! V = MultiDimVar({"A"}, [4], indexOrder);
%! expected_output = ["Indices: A \n", ...
%!                    "   0\n",...
%!                    "   0\n",...
%!                    "   0\n",...
%!                    "   0\n"];
% ACTION
%! test_output = evalc('disp(V)');
% ASSERT
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing disp of a vector with values ##
% SETUP
%! V = MultiDimVar({"A"}, [4], indexOrder, [1;2;3;4]);
%! expected_output = ["Indices: A \n", ...
%!                    "   1\n",...
%!                    "   2\n",...
%!                    "   3\n",...
%!                    "   4\n"];
% ACTION
%! test_output = evalc('disp(V)');
% ASSERT
%! assert(isequal(test_output, expected_output))

%!test
%! ## Testing disp of an empty 2D matrix ##
% SETUP
%! M = MultiDimVar({"A", "B"}, [4, 3], indexOrder);
%! expected_output = ["Indices: A B \n", ...
%!                    "   0   0   0\n",...
%!                    "   0   0   0\n",...
%!                    "   0   0   0\n",...
%!                    "   0   0   0\n"];
% ACTION
%! test_output = evalc('disp(M)');
% ASSERT
%! assert(isequal(test_output, expected_output))
