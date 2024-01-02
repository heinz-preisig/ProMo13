function self = cos(op1)
  self = MultiDimVar(op1.indexLabels, size(op1), cos(op1.value));
endfunction