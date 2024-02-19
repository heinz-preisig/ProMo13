function self = times(op1, op2)
  % Type verification
  assert(isa(op1, 'MultiDimVar') || isscalar(op1),
    'Error: Inputs must be of type MultiDimVar or a scalar');
  assert(isa(op2, 'MultiDimVar') || isscalar(op2),
    'Error: Inputs must be of type MultiDimVar or a scalar');

  % Convert scalar inputs to MultiDimVar objects.
  if ~isa(op1, "MultiDimVar") && isscalar(op1)
    op1 = MultiDimVar({}, [1], op2.indexOrder, [op1]);
  endif

  if ~isa(op2, "MultiDimVar") && isscalar(op2)
    op2 = MultiDimVar({}, [1], op1.indexOrder, [op2]);
  endif

  % Both operand are expanded so their indexLabels are the union of the
  % individual indexLabels.
  % First: the position of the existing indexLabels is addded to the
  % dimOrder array.
  [~, dimOrder1] = ismember(op1.indexOrder, op1.indexLabels); 
  [~, dimOrder2] = ismember(op2.indexOrder, op2.indexLabels);
  existingIndicesPositions = dimOrder1 | dimOrder2;

  % Second: arrays are filtered eliminating dimensions corresponding to
  % missing indices in both operands.
  indexLabels = op1.indexOrder(existingIndicesPositions);
  if isempty(indexLabels)
    indexLabels = {};
  endif

  dimOrder1 = dimOrder1(existingIndicesPositions);
  dimOrder2 = dimOrder2(existingIndicesPositions);

  % Third: missing dimensions are substituted for singleton dimensions.
  extraDim1 = numel(op1.indexLabels) + 1;
  extraDim2 = numel(op2.indexLabels) + 1;

  for i = 1:numel(indexLabels)
    if ~dimOrder1(i)
      dimOrder1(i) = extraDim1;
      extraDim1 = extraDim1 + 1;
    endif
    if ~dimOrder2(i)
      dimOrder2(i) = extraDim2;
      extraDim2 = extraDim2 + 1;
    endif
  endfor

  % Rearrangement of the matrices if is needed
  if numel(indexLabels) >= 2 % Permute requires dimOrder length to be at least 2
    op1Value = permute(op1.value, dimOrder1);
    op2Value = permute(op2.value, dimOrder2);
  else
    op1Value = op1.value;
    op2Value = op2.value;
  endif

  value = op1Value .* op2Value;
  self = MultiDimVar(indexLabels, size(value), op1.indexOrder, value);
endfunction