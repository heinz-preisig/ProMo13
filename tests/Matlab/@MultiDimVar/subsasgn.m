function self = subsasgn(self, s, varargin)
  switch s(1).type
    case '()'
      if length(s) == 1
        rhs = varargin{1};

        % If the rhs is a MultiDimVar then we assign its Value.
        if isa(rhs, "MultiDimVar")
          rhs = rhs.value;
        else
          assert(
            ismatrix(rhs) | isscalar(rhs),
            "Wrong type. Only scalars, matrices and other MultiDimVar\n",...
            "objects can be assigned to MultiDimVar objects."
          )
        endif

        % Checking that the dimensions are the same.
        blockS = s;
        nDimensions = length(s(1).subs);
        for i = 1:nDimensions
          indexingInfo = s(1).subs{i};
          % Indexing information expanded to account for blocks.
          blockS(1).subs{i} = [self.indexBlocks{i}{indexingInfo}];
        endfor

        sizeSelf = size(builtin("subsref", self.value, blockS));
        sizeRhs = size(rhs);

##        assert(
##          isequal(sizeSelf, sizeRhs),
##          "In MultiDimVar.subsasgn():\n",...
##          "Nonconformant arguments (op1 is %s, op2 is %s)",
##          formatsize(subsref(self, s)), formatsize(varargin{1})
##        )
        self.value = builtin("subsasgn", self.value, blockS, rhs);
      else
        % Use built-in for any other expression
        self = builtin('subsasgn', self, s, varargin{:});
      endif
    case '.'
      self = builtin('subsasgn', self, s, varargin{:});
    case '{}'
      self = builtin('subsasgn', self, s, varargin{:});
    otherwise
      error('Not a valid indexing expression')
  endswitch
endfunction