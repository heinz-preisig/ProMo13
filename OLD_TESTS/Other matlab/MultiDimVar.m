classdef MultiDimVar
  properties
    Value
    IndexLabels
    IndexSets
  endproperties
  methods
    function obj = MultiDimVar(val, indexlabels, indexsets)
      obj.Value = val;
      obj.IndexLabels = indexlabels;
      obj.IndexSets = indexsets;
    endfunction
    function str = disp(obj)
      str{1} = sprintf("\n%s: \n%s","Value",disp(obj.Value));
      str{2} = "Index Sets:\n";

      for i = 1:size(obj.IndexLabels, 2)
        str{i+2} = sprintf("%s: %s", obj.IndexLabels{i}, disp(obj.IndexSets{i}));
      endfor
      str = sprintf('%s\n',str{:});
    endfunction
    function output = subsref(obj,s);
      switch s(1).type
        case '()'
          if length(s) == 1
            new_obj = MultiDimVar(builtin('subsref',obj.Value,s), obj.IndexSets);
            % [varargout{1:nargout}] = builtin('subsref',obj.Value,s)
          endif
          return
        case '.'
          output = builtin('subsref',obj,s);
          return
        otherwise
          error('Not a valid indexing expression')
      endswitch
    endfunction
  endmethods
endclassdef

function pr = ProductReduce(A, B, red_set)
  dim = 2;
  pr_idx_lbls = cell(1, dim);
  pr_idx_sets = cell(1, dim);

  if isequal(red_set, A.IndexLabels{1})
    A_value = A.Value';
    pr_idx_lbls{1} = A.IndexLabels{2};
    pr_idx_sets{1} = A.IndexSets{2};
  elseif isequal(red_set, A.IndexLabels{2})
    A_value = A.Value;
    pr_idx_lbls{1} = A.IndexLabels{1};
    pr_idx_sets{1} = A.IndexSets{1};
  else
    error("redset is not an Index in the matrix A")
  endif

  if isequal(red_set, B.IndexLabels{1})
    B_value = B.Value;
    pr_idx_lbls{2} = B.IndexLabels{2};
    pr_idx_sets{2} = B.IndexSets{2};
  elseif isequal(red_set, B.IndexLabels{2})
    B_value = B.Value';
    pr_idx_lbls{2} = B.IndexLabels{1};
    pr_idx_sets{2} = B.IndexSets{1};
  else
    error("redset is not an index in the matrix B")
  endif

  pr = MultiDimVar(A_value*B_value, pr_idx_lbls, pr_idx_sets);
endfunction
