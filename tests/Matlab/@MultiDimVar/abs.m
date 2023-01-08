function self = abs(op1)
  self = MultiDimVar(op1.indexLabels, op1.indexSets, abs(op1.value));
endfunction