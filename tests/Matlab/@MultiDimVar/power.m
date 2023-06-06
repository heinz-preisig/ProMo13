function self = power(op1, op2)
##  assert(
##    isequal(size(op1), size(op2)),
##    error(
##      "In MultiDimVar.power(): Nonconformant arguments (op1 is %s, op2 is %s)",
##      formatsize(op1), formatsize(op2)
##    )
##  )

  self = MultiDimVar(op1.indexLabels, op1.indexSets, op1.value .^ op2.value);
endfunction