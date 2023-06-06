function self = product(op1, reduceSet)
  isReduceSetInOp1 = strcmp(op1.indexLabels, reduceSet);

##  assert(
##    any(isReduceSetInOp1),
##    "reduceSet is not an indexSet in op1"
##  )
  reduceSetPos1 = find(isReduceSetInOp1);

  value = prod(op1.value, reduceSetPos1);
  # Vectors are always column vectors.
  if isrow(value)
    value = value';
  endif

  # We delete the cell containing the information about reduceSet
  indexLabels = op1.indexLabels;
  indexLabels(reduceSetPos1) = [];
  indexSets = op1.indexSets;
  indexSets(reduceSetPos1) = [];

  self = MultiDimVar(indexLabels, indexSets, value);
endfunction