classdef MultiDimVar
  properties
    value
    indexLabels
    indexSets
    indexBlocks
  endproperties
  methods
    function self = MultiDimVar(varargin)
      self.indexLabels = varargin{1};
      self.indexSets = varargin{2};
      % The interval data for each of the blocks is stored independently.
      self.indexBlocks = cell(size(self.indexSets));
      size_vector = zeros(1, size(self.indexSets, 2));
      for i = 1:size(self.indexSets, 2)
        self.indexBlocks{i} = cell(size(self.indexSets{i}));
        ini = 1;
        fin = 1;
        for j = 1:size(self.indexSets{i}, 2)
          fin = ini + size(self.indexSets{i}{j}, 2) - 1;
          self.indexBlocks{i}{j} = [ini:fin];
          ini = fin + 1;
        endfor
        size_vector(i) = fin;
      endfor
      if nargin < 3
        if isscalar(size_vector)
          self.value = zeros(size_vector, 1);
        else
          self.value = zeros(size_vector);
        endif
      else
        self.value = varargin{3};
      endif
    endfunction
    
    % Subscripted assignment and reference
    self = subsref(self, s)
    self = subsasgn(self, s, varargin)
    % Auxiliary functions
    fvarargout = size(self, varargin)
    bool = isscalar(self)
    bool = isvector(self)
    str = disp(op1)
    str = formatsize(op1)
    % Unitary functions and operators
    self = abs(op1)
    self = ctranspose(op1)
    self = sign(op1)
    self = reciprocal(op1)
    self = product(op1, reduceSet)
    self = sparse(op1)
    % Binary functions and operators
    self = plus(op1, op2)
    self = minus(op1, op2)
    self = times(op1, op2)
    self = rdivide(op1, op2)
    self = reduceproduct(op1, reduceSet, op2)
    self = expandproduct(op1, op2)
    self = blockreduce(op1, reduceSet, targetSet, op2)
    self = khatrirao(op1, op2)
  endmethods
endclassdef


