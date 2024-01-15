function self = subsasgn(self, s, varargin)
  switch s(1).type
    case '()'
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
      % Try to access the values to catch out of bounds errors.
      % In matlab the default action is to resize the matrix but we dont allow
      % for it.
      test = subsref(self, s);
      
      self.value = builtin("subsasgn", self.value, s(1), rhs);
    case '.'
      self = builtin('subsasgn', self, s, varargin{:});
    case '{}'
      self = builtin('subsasgn', self, s, varargin{:});
    otherwise
      error('Not a valid indexing expression')
  endswitch
endfunction