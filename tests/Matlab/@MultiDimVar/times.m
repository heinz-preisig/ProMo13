function self = times(op1, op2)
  if isscalar(op1) || isscalar(op2)
    % Case: a .* b_x or b_x .* a -> c_x    (N-dimensional matrix)
    option = 1; 
  elseif strcmp(op1.indexLabels, op2.indexLabels)
    % Case: a_x .* b_x -> c_x              (N-dimensional matrices)
    option = 1;
  else
    [commonLabels, iOp1, iOp2] = intersect(op1.indexLabels, op2.indexLabels);   
  
    if length(commonLabels) > 0
      % Only for a vector and a 2-dimesional matrix
      if iOp1 == iOp2
        % Case: a_x .* b_x,y or b_x,y .* a_x -> c_x,y
        option = 1
      elseif isvector(op1)
        % Case: a_y .* b_x,y -> c_x,y
        option = 2;
      else
        % Case: b_x,y .* a_y -> c_x,y
        option = 3;
      endif
    else
      % Case a_x .* b_y,z -> c_x,y,z        (N-dimensional matrices)
      option = 4;
    endif
  endif
  
  switch option
    case 1
      self = mdvTimes();
    case 2
      self = mdvTimes(); 
    case 3
      self = mdvTimes();
    case 4
      sizeOp1 = size(op1);
      sizeOp2 = size(op2);
      % The dimension of the result is obtained by adding the dimensions
      % of both operands. 
      value = zeros([sizeOp1, sizeOp2]);

      % Cell array containing ":" for each of the dimensions of the result.
      indexes = repmat({':'}, 1, length(size(value)));

      % We use linear indexes to loop through all elements of op1. Then we
      % convert to subscripts and replace the necesary elements in indexes.
      % Finally the multiplication of the ith element of op1 by the whole
      % op2 is assigned to the position indicated by indexes.
      for i = 1:prod(sizeOp1)
        [indexes{1:length(sizeOp1)}] = ind2sub(sizeOp1, i);
        value(indexes{:}) = op1.value(i) .* op2.value;
      endfor
  
      indexLabels = cat(2, op1.indexLabels, op2.indexLabels);
      indexSets = cat(2, op1.indexSets, op2.indexSets);

      % We use squeeze to account for the vectors having 2 dimensions in 
      % matlab and thus adding a dimension 1 in the middle if op1 is a
      % vector instead of a matrix.
      self = MultiDimVar(indexLabels, indexSets, squeeze(value));
  endswitch
  
  function self = mdvTimes()
    if isscalar(op1)
      indexLabels = op2.indexLabels;
      indexSets = op2.indexSets;
    elseif isscalar(op2)
      indexLabels = op1.indexLabels;
      indexSets = op1.indexSets;
    elseif isvector(op1)
      indexLabels = op2.indexLabels;
      indexSets = op2.indexSets;
    else
      indexLabels = op1.indexLabels;
      indexSets = op1.indexSets;
    endif
    
    switch option
      case 1
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
      case 2
        op1Value = op1.value';
        op2Value = op2.value;
      case 3
        op1Value = op1.value;
        op2Value = op2.value';
    endswitch

    self = MultiDimVar(indexLabels, indexSets, op1Value .* op2Value);
  endfunction 
endfunction