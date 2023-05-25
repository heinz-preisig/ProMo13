function self = rdivide(op1, op2)
##  if ~ (isscalar(op1) | isscalar(op2) | isequal(size(op1), size(op2)))
##    error(
##      "In MultiDimVar.rdivide():\n\
##       Nonconformant arguments (op1 is %s, op2 is %s)",
##      formatsize(op1), formatsize(op2)
##    )
##  endif

  if isscalar(op1)
    indexLabels = op2.indexLabels;
    indexSets = op2.indexSets;
  else
    indexLabels = op1.indexLabels;
    indexSets = op1.indexSets; 
  endif
  
  % To account for scalars that are not MultiDimVar
  if isa(op1, "MultiDimVar")
    op1Value = op1.value;
  else
    op1Value = op1;
  endif
  if isa(op2, "MultiDimVar")
    op2Value = op2.value;
  else
    op2Value = op2;
  endif

  self = MultiDimVar(indexLabels, indexSets, op1Value ./ op2Value);
endfunction