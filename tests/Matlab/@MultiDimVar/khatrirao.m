function self = khatrirao(op1, op2)
  % op1 and op2 are matrices
  % Every set in splitSet1 is a subset of one of the sets in splitSet2. 
  % The order is not important. Ex. {"N", "A"} and {"AS", "NS"}.
  % Only VALID for up to 2 dimensions.

  % posIndex is used to understand the relative position of the indexes
  % of op1 and op2. It stores in what position the first index of op1
  % is in op2. otherIndex stores the remaining dimension if op2 is a 2D
  % matrix. 
  
  splitSet1 = op1.indexLabels;
  splitSet2 = op2.indexLabels;


  % Using this as octave have not implemented the function contains()
  posIndex = find(not(cellfun('isempty',strfind(splitSet2, splitSet1{1}))));
  otherIndex = 3 - posIndex;

  if posIndex == 2
    op1 = op1';
  endif

  self = MultiDimVar(op2.indexLabels, op2.indexSets, zeros(size(op2)));
  s = substruct("()", {});

  if length(splitSet1) == 1
    if length(splitSet2) == 1         %             op1_x : op2_xz
      % fprintf("Case 1: op1_x : op2_xz\n");
      for i = 1:length(op2.indexSets{1})
        s(1).subs = cell(1, 1);
        s(1).subs{1} = i;
        self = subsasgn(self, s, op1.value(i) * subsref(op2, s).value);
        % disp(self)
      endfor
    else                              %     (op1_x|op1_y) : op2_xz_yz
      % fprintf("Case 2: (op1_x|op1_y) : op2_xz_yz\n")
      for i = 1:length(op2.indexSets{posIndex})
        s(1).subs = cell(1, 2);
        s(1).subs{posIndex} = i;
        s(1).subs{otherIndex} = ":";
        self = subsasgn(self, s, op1.value(i) * subsref(op2, s).value);
      endfor
    endif
  else                                % (op1_x_y|op1_y_x) : op2_xz_yz
    % fprintf("Case 3: (op1_x_y|op1_y_x) : op2_xz_yz\n")
    for i = 1:length(op2.indexSets{1})
      for j = 1:length(op2.indexSets{1})
        s(1).subs = cell(1, 2);
        s(1).subs{1} = i;
        s(1).subs{2} = j;
        self = subsasgn(self, s, op1.value(i, j) * subsref(op2, s).value);
      endfor
    endfor
  endif
endfunction