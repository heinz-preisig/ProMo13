function bool = isequal(op1, op2)
  assert(
    isa(op1, "MultiDimVar") && isa(op2, "MultiDimVar"),
    "Error: Both operands need to be of type MultiDimVar"
  )
  if ~isequal(size(op1), size(op2))
    bool = false;
    return
  endif

  bool = isequal(op1.indexLabels, op2.indexLabels) && (op1.value == op2.value);
endfunction