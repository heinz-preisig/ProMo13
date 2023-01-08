function self = ctranspose(op1)
  % We always have column vectors so transpose will return the same vector.
  % Operations that require transpose will do so on the vale of the object.
  if isscalar(op1) | isvector(op1)
    self = op1;
    return
  endif

  value = op1.value';
  indexLabels([1 2]) = op1.indexLabels([2 1]);
  indexSets([1 2]) = op1.indexSets([2 1]);

  self = MultiDimVar(indexLabels, indexSets, value);
endfunction