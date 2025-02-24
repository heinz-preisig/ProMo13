%!shared indexOrder
%! indexOrder = {"A", "B"};


%!error <Error: Both operands need to be of type MultiDimVar>
%! ## Testing eq with element of wrong type ##
% SETUP
%! V1 = MultiDimVar({"A"}, [3], indexOrder);
%! V2 = [0; 0; 0];
% ACTION
%! isequal(V1, V2)

%!xtest <## Testing eq with vectors (different indexLabels) ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [3], indexOrder);
%! V2 = MultiDimVar({"B"}, [3], indexOrder);
%! expected_output = false;
% ACTION
%! test_output = isequal(V1, V2);
% ASSERT
%! assert(test_output == expected_output)

%!xtest <## Testing eq with vectors (different sizes) ##>
% SETUP
%! V1 = MultiDimVar({"A"}, [3], indexOrder, [1; 2; 3]);
%! V2 = MultiDimVar({"A"}, [4], indexOrder, [1; 2; 3;4]);
%! expected_output = false;
% ACTION
%! test_output = isequal(V1, V2);
% ASSERT
%! assert(test_output == expected_output)



