function self = mtimes(op1, op2)
  assert(
    isa(op1, "MultiDimVar") && isa(op2, "MultiDimVar"),
    "Error: Both operands need to be of type MultiDimVar"
  )
  commonIndex = intersect(op1.indexLabels, op2.indexLabels);

  assert(~isempty(commonIndex), "Error: No common indices.");
  assert(length(commonIndex) == 1, "Error: Too many common indices");

  % Position of the reduce set in both operands
  reduceSetPos1 = find(strcmp(commonIndex(1), op1.indexLabels));
  reduceSetPos2 = find(strcmp(commonIndex(1), op2.indexLabels));

  assert(size(op1)(reduceSetPos1) == size(op2)(reduceSetPos2),
    "Error: Nonconformant arguments (op1 is %s, op2 is %s)",
    num2str(size(op1)), num2str(size(op2)))

  % The resulting indexSet is a cat of the indexSets of both operators
  % keeping the order and removing reduceSet.
  indexLabels = cat(
    2,
    op1.indexLabels(1:end ~= reduceSetPos1),
    op2.indexLabels(1:end ~= reduceSetPos2)
  );

  % TODO: Substitute this for tensorprod to handle higher dimensions
  % Waiting for octave to add the patch where is implemented.
  
  % Transposing if necessary before the multiplication.
  % Only for up to 2 dimensions.
  if reduceSetPos1 == 1
    op1Value = op1.value';
  else
    op1Value = op1.value;
  endif
  if reduceSetPos2 == 2
    op2Value = op2.value';
  else
    op2Value = op2.value;
  endif

  value = op1Value * op2Value;

  # Vectors are always column vectors.
  if isrow(value)
    value = value';
  endif

  self = MultiDimVar(indexLabels, size(value), value);
endfunction