function self = times(op1, op2)
  if isscalar(op1) || isscalar(op2)
    % Scalars are converted to MultDimVar objects and the operation is
    % always valid.
    if ~isa(op1, "MultiDimVar")
      op1 = MultiDimVar({}, [1], op2.indexOrder, [op1]);
    endif
    if ~isa(op2, "MultiDimVar")
      op2 = MultiDimVar({}, [1], op1.indexOrder, [op2]);
    endif

    value = op1.value .* op2.value;
    if length(op1.indexLabels) > length(op2.indexLabels)
      indexLabels = op1.indexLabels;
    else
      indexLabels = op2.indexLabels;
    endif
  elseif isequal(op1.indexLabels, op2.indexLabels)
    % Classic Hadamard case indexLabels and sizes match.
    assert(
      isequal(size(op1), size(op2)),
      "Error: Nonconformant arguments (op1 is %s, op2 is %s)",
      formatsize(op1), formatsize(op2)
    )
    
    indexLabels = op1.indexLabels;
    value = op1.value .* op2.value;
  else
    % One of the operands might need to be expanded, only valid if all
    % the index labels of the operand that need to be expanded exist in
    % the other operand.

    % Convenience rearrangement so the operand that needs to be expanded
    % is op1.
    if length(op1.indexLabels) > length(op2.indexLabels)
      temp = op1;
      op1 = op2;
      op2 = temp;
    endif

    % Building the array used for the permutation in the case where the
    % indexLabels dont have the same size
    dimorder = zeros(size(op2.indexLabels));
    for i=1:length(op1.indexLabels)
      pos = find(strcmp(op1.indexLabels{i}, op2.indexLabels));
      assert(~isempty(pos),"Error: Label (%s) not found in second argument",
          op1.indexLabels{i})
      
      dimorder(pos) = i;
    endfor

    % The index labels in op2 that are not in op1 receive dimension
    % numbers that didnt exist in op1, we make use of the fact that
    % there are infinite dimensions of size 1 for each matrix, in that
    % way the unexisting indexLabels are represented as dimensions of
    % size 1.
    cont = length(op1.indexLabels) + 1;
    for i=1:length(dimorder)
      if dimorder(i) == 0
        dimorder(i) = cont;
        cont = cont + 1;
      endif
    endfor

    value1Perm = permute(op1.value, dimorder);

    % After both operands have the same dimensions we check the sizes of
    % each. For this product to work the sizes for all dimensions in
    % both operands need to match or be 1.
    size1 = size(value1Perm);
    size2 = size(op2);
    for i=1:length(size1)
      assert(size1(i) == size2(i) || size1(i) == 1,
        "Error: Nonconformant arguments (op1 is %s, op2 is %s)",
        formatsize(op1), formatsize(op2))
    endfor

    value = value1Perm .* op2.value;
    indexLabels = op2.indexLabels;
  endif

  self = MultiDimVar(indexLabels, size(value), op1.indexOrder, value);
endfunction