function self = expandproduct(op1, op2)
  assert(
    isa(op1, "MultiDimVar") && isa(op2, "MultiDimVar"),
    "Error: Both operands need to be of type MultiDimVar."
  )
  commonIndex = intersect(op1.indexLabels, op2.indexLabels);
  assert(isempty(commonIndex), "Error: Common indices found.");

  value = squeeze(reshape(op1.value(:) * op2.value(:).', [size(op1), size(op2)]));
  indexLabels = [op1.indexLabels, op2.indexLabels];

  self = MultiDimVar(indexLabels, size(value), op1.indexOrder, value);
endfunction