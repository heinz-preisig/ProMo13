function self = reduceproduct(op1, op2, reduceIndex)
  % To use when there are 2 common indices but the reduction
  % only uses one. At least one of the operators is 3D. The other one
  % is 1D, 2D or 3D.

  assert(
    isa(op1, "MultiDimVar") && isa(op2, "MultiDimVar"),
    "Error: Both operands need to be of type MultiDimVar"
  )
  commonIndices = intersect(op1.indexLabels, op2.indexLabels);

  assert(~isempty(commonIndices), "Error: No common indices.");
  assert(length(commonIndices) == 2,
    "Error: Wrong number of common indices. Expecting 2 found %d",
    length(commonIndices))

  otherCommonIndex = commonIndices{~strcmp(commonIndices, reduceIndex)};

  % Position of the common index that is not reduced in both operands
  otherCommonIndexPos1 = find(strcmp(otherCommonIndex, op1.indexLabels));
  otherCommonIndexPos2 = find(strcmp(otherCommonIndex, op2.indexLabels));
  
  % Position of the reduce set in both operands
  reduceIndexPos1 = find(strcmp(reduceIndex, op1.indexLabels));
  reduceIndexPos2 = find(strcmp(reduceIndex, op2.indexLabels));

  assert(size(op1)(reduceIndexPos1) == size(op2)(reduceIndexPos2),
    "Error: Nonconformant arguments (op1 is %s, op2 is %s)",
    num2str(size(op1)), num2str(size(op2)))

  % Maximum 3 dimensions
  independentIndexPos1 = 6 - (otherCommonIndexPos1 + reduceIndexPos1);
  independentIndexPos2 = 6 - (otherCommonIndexPos2 + reduceIndexPos2);
  
  % For the permute function
  dimOrder1 = [independentIndexPos1, reduceIndexPos1, otherCommonIndexPos1];
  dimOrder2 = [reduceIndexPos2, independentIndexPos2, otherCommonIndexPos2];
  
  % Reorganizing the indices
  op1Value = permute(op1.value, dimOrder1);
  op2Value = permute(op2.value, dimOrder2);

  % Calculating the size for the result
  resultSize = size(op1Value);
  resultSize(2) = size(op2Value)(2);

  value = zeros(resultSize);

  % Doing matrix multiplication per page
  for i = 1:resultSize(3)
    value(:,:,i) = op1Value(:,:,i) * op2Value(:,:,i);
  endfor

  value = squeeze(value);

  % Building the labels for the result
  indexLabels = {"", "", op1.indexLabels{otherCommonIndexPos1}};

  % Adding labels if they belong to non singleton dimensions
  if independentIndexPos1 <= length(op1.indexLabels)
    indexLabels(1) = op1.indexLabels{independentIndexPos1};
  endif
  if independentIndexPos2 <= length(op2.indexLabels)
    indexLabels(2) = op2.indexLabels{independentIndexPos2};
  endif
  indexLabels = indexLabels(~cellfun('isempty', indexLabels));

  self = MultiDimVar(indexLabels, resultSize, op1.indexOrder, value);
endfunction