function str = disp(op1)
  str{1} = sprintf("\n%s: \n%s", "Value", disp(op1.value));
  str{2} = "Index Sets:\n";

  for i = 1:size(op1.indexLabels, 2)
    str{i+2} = sprintf("%s: %s", op1.indexLabels{i}, disp(op1.indexSets{i}));
  endfor
  str = sprintf('%s',str{:});
endfunction