classdef MultiDimVar < matlab.mixin.indexing.RedefinesParen
  properties (Access=private)
    Value
    IndexSets
  endproperties
  methods
    function obj = ArrayWithLabel(val, indexsets)
      obj.Value = val;
      obj.IndexSets = indexsets;
    endfunction
  endmethods
  methods (Access=protected)
    function varargout = parenReference(obj, indexOp)
      obj.Value = obj.Value.(indexOp(1));
      if isscalar(indexOp)
        varargout{1} = obj;
        return;
      endif
      [varargout{1:nargout}] = obj.(indexOp(2:end));
    endfunction
    function obj = parenAssign(obj,indexOp,varargin)
    % Ensure object instance is the first argument of call.
      if isempty(obj)
        obj = varargin{1};
      endif
      if isscalar(indexOp)
        assert(nargin==3);
        rhs = varargin{1};
        obj.Value.(indexOp) = rhs.Value;
        return;
      endif
      [obj.(indexOp(2:end))] = varargin{:};
    endfunction
    function n = parenListLength(obj,indexOp,ctx)
      if numel(indexOp) <= 2
        n = 1;
        return;
      endif
      containedObj = obj.(indexOp(1:2));
      n = listLength(containedObj,indexOp(3:end),ctx);
    endfunction
    function obj = parenDelete(obj,indexOp)
      obj.Value.(indexOp) = [];
    endfunction
  endmethods
  methods (Access=public)
    function out = value(obj)
      out = obj.Value;
    endfunction        
    function out = cat(dim,varargin)
      numCatArrays = nargin-1;
      newArgs = cell(numCatArrays,1);
      for ix = 1:numCatArrays
        if isa(varargin{ix},'MultiDimVar')
          newArgs{ix} = varargin{ix}.Value;
        else
          newArgs{ix} = varargin{ix};
        endif
      endfor
      out = MultiDimVar(cat(dim,newArgs{:}));
    endfunction
    function varargout = size(obj,varargin)
      [varargout{1:nargout}] = size(obj.Value,varargin{:});
    endfunction
  endmethods
  methods (Static, Access=public)
    function obj = empty()
      obj = MultiDimVar([]);
    endfunction
  endmethods
endclassdef
