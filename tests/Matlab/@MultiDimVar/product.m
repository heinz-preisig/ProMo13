function self = product(op1, reduceLabel)
  isReduceSetInOp1 = strcmp(op1.indexLabels, reduceLabel);

  assert(
    any(isReduceSetInOp1),
    "%s is not an indexSet in %s", reduceLabel, inputname(1)
  )

  reduceSetPos = find(isReduceSetInOp1);

  indexLabels = op1.indexLabels;
  indexLabels(reduceSetPos) = [];
  if isempty(indexLabels)
    indexLabels = {};
  endif

  % Remove the dimensions of size 1 of the result.
  value = squeeze(prod(op1.value, reduceSetPos));
  # Vectors are always column vectors.
  if isrow(value)
    value = value';
  endif

  self = MultiDimVar(indexLabels, size(value), value);
endfunction