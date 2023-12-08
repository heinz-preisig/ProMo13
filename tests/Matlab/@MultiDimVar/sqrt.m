function self = sqrt(op1)
  self = MultiDimVar(op1.indexLabels, size(op1), sqrt(op1.value));
endfunction