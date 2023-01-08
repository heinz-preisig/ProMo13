function varargout = size(self, varargin)
  [varargout{1:nargout}] = builtin('size', self.value, varargin{:});
end
