function self = expandproduct(op1, op2)
  sizeOp1 = size(op1);
  sizeOp2 = size(op2);

  % The dimension of the result is obtained by adding the dimensions
  % of both operands. 
  value = zeros([sizeOp1, sizeOp2]);

  % Cell array containing ":" for each of the dimensions of the result.
  indexes = repmat({':'}, 1, length(size(value)))

  % We use linear indexes to loop through all elements of op1. Then we
  % convert to subscripts and replace the necesary elements in indexes.
  % Finally the multiplication of the ith element of op1 by the whole
  % op2 is assigned to the position indicated by indexes.
  for i = 1:prod(sizeOp1)
    [indexes{1:length(sizeOp1)}] = ind2sub(sizeOp1, i);
    value(indexes{:}) = op1.value(i) .* op2.value;
  endfor
  
  indexLabels = cat(2, op1.indexLabels, op2.indexLabels);
  indexSets = cat(2, op1.indexSets, op2.indexSets);

  % We use squeeze to account for the vectors having 2 dimensions in 
  % matlab and thus adding a dimension 1 in the middle if op1 is a
  % vector instead of a matrix.
  self = MultiDimVar(indexLabels, indexSets, squeeze(value));
endfunction