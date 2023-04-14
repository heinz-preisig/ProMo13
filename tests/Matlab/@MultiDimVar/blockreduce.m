function self = blockreduce(op1, reduceSet, targetSet, op2)
  % op1 is always a column vector
  % op2 is a block matrix with targetSet as one of the indexLabels

  targetIndex = find(strcmp(op2.indexLabels, targetSet));
  otherIndex = 3 - targetIndex; % 3 - 1 = 2; 3 - 2 = 1 :)

  resultSize = zeros(1, 2);
  resultSize(targetIndex) = length(op2.indexSets{targetIndex});
  resultSize(otherIndex) = size(op2, otherIndex);

  value = zeros(resultSize);

  s = substruct("()", {});

  if isequal(op1.indexLabels{1}, targetSet)
    if targetIndex == 1                     % Case A_xs|s in xs|B_xs_y
      for i = 1:resultSize(targetIndex)
        s(1).subs = {i};
        term1 = subsref(op1, s);

        s(1).subs = {i, ":"};
        term2 = subsref(op2, s);
      
        value(i, :) = term1.value' * term2.value;
      endfor
    else                                    % Case A_xs|s in xs|B_y_xs
      for i = 1:resultSize(targetIndex)
        s(1).subs = {i};
        term1 = subsref(op1, s);

        s(1).subs = {":", i};
        term2 = subsref(op2, s);
      
        value(:, i) = term2.value * term1.value;
      endfor
    endif
  else
    if targetIndex == 1                     % Case A_s|s in xs|B_xs_y
      for i = 1:resultSize(targetIndex)
        s(1).subs = {op2.indexSets{targetIndex}{i}};
        term1 = subsref(op1, s);

        s(1).subs = {i, ":"};
        term2 = subsref(op2, s);

        value(i, :) = term1.value' * term2.value;
      endfor
    else                                    % Case A_s|s in xs|B_y_xs
      for i = 1:resultSize(targetIndex)
        s(1).subs = {op2.indexSets{targetIndex}{i}};
        term1 = subsref(op1, s);

        s(1).subs = {":", i};
        term2 = subsref(op2, s);

        value(:, i) = term2.value * term1.value;
      endfor
    endif
  endif

  indexSets = op2.indexSets;
  indexSets{targetIndex} = {1:resultSize(targetIndex)};
  indexLabels = op2.indexLabels;
  indexLabels{targetIndex} = erase(indexLabels{targetIndex}, reduceSet);
  self = MultiDimVar(indexLabels, indexSets, value);
endfunction