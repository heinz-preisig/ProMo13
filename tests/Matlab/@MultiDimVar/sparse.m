function self = sparse(op1)
  self = MultiDimVar(op1.indexLabels, op1.indexSets, sparse(op1.value));
endfunction