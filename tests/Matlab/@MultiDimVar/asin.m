function self = asin(op1)
  self = MultiDimVar(op1.indexLabels, size(op1), asin(op1.value));
endfunction