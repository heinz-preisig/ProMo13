function self = log(op1)
  self = MultiDimVar(op1.indexLabels, size(op1), log(op1.value));
endfunction