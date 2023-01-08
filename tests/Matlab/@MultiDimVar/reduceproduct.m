function self = reduceproduct(op1, reduceSet, op2)
  isReduceSetInOp1 = strcmp(op1.indexLabels, reduceSet);
  isReduceSetInOp2 = strcmp(op2.indexLabels, reduceSet);

  assert(
    any(isReduceSetInOp1),
    "reduceSet is not an indexSet in op1"
  )
  assert(
    any(isReduceSetInOp2),
    "reduceSet is not an indexSet in op2"
  )

  % The resulting indexSet is a cat of the indexSets of both operators
  % keeping the order and removing reduceSet.
  reduceSetPos1 = find(isReduceSetInOp1);
  reduceSetPos2 = find(isReduceSetInOp2);
  indexLabels = cat(
    2,
    op1.indexLabels(1:end ~= reduceSetPos1),
    op2.indexLabels(1:end ~= reduceSetPos2)
  );
  indexSets = cat(
    2,
    op1.indexSets(1:end ~= reduceSetPos1),
    op2.indexSets(1:end ~= reduceSetPos2)
  );

  % Transposing if necessary before the multiplication.
  % Only for up to 2 dimensions.
  if reduceSetPos1 == 1
    op1 = op1';
  endif
  if reduceSetPos2 == 2
    op2 = op2';
  endif

  value = op1.value * op2.value;

  # Vectors are always column vectors.
  if isrow(value)
    value = value';
  endif

  self = MultiDimVar(indexLabels, indexSets, value);
endfunction