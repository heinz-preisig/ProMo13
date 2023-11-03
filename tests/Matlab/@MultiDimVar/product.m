function self = product(op1, reduceSet)
  isReduceSetInOp1 = strcmp(op1.indexLabels, reduceSet);

##  assert(
##    any(isReduceSetInOp1),
##    "reduceSet is not an indexSet in op1"
##  )
  if any(isReduceSetInOp1)
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
  else
    reduceSetPos = -1;
    block_index_regex = '(\w+)_x_(\w+)';
    for i=1:length(op1.indexLabels)
      matches = regexp(op1.indexLabels{i}, block_index_regex,'tokens', 'once')
      if ~isempty(matches)
        if strcmp(matches{2}, reduceSet)
          reduceSetPos = i;
          leftOverIndexLabel = matches{1};
        endif
      endif
    endfor

    dimensions = ndims(op1.value)

    newIdx = cell(1, dimensions);
    oldIdx = cell(1, dimensions);
    for j=1:dimensions
      if j ~= reduceSetPos
        newIdx{j} = ':';
        oldIdx{j} = ':';
      endif
    endfor
    
    oldSize = size(op1.value);
    newSize = oldSize;
    newSize(reduceSetPos) = length(op1.indexBlocks{reduceSetPos});
    newValue = zeros(newSize);
    newIndexSets = op1.indexSets;
    for i=1:length(op1.indexBlocks{reduceSetPos});
      newIdx{reduceSetPos} = i;
      oldIdx{reduceSetPos} = op1.indexBlocks{reduceSetPos}{i};
      newIndexSets{reduceSetPos}{i} = i;
      newValue(newIdx{:}) = prod(op1.value(oldIdx{:}), reduceSetPos);
    endfor
    newIndexLabels = op1.indexLabels;
    newIndexLabels{reduceSetPos} = leftOverIndexLabel;

    self = MultiDimVar(newIndexLabels, newIndexSets, newValue);
  endif
endfunction