function self = sign(op1)
  self = MultiDimVar(op1.indexLabels, op1.indexSets, sign(op1.value));
endfunction