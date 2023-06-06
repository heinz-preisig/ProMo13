function self = subsref(op1, s)
  switch s(1).type
    case '()'
      blockS = s(1);
      indexSets = cell(size(op1.indexSets));
      nDimensions = length(s(1).subs);

      selfDimensions = length(indexSets);
      % Extra dimensions can only be indexed by 1 or ":"
      % Ex: In a vector a(3) is the same as a(3, 1) or a(3, :).
      if nDimensions > selfDimensions
        extraIndexes = s(1).subs((selfDimensions + 1):end);
        extraIndexesStr = cellfun(@num2str, extraIndexes, 'un', 0);

##        assert(
##          all(strcmp(extraIndexesStr, ":") | strcmp(extraIndexesStr, "1")), 
##          'Indexing error: Size is %s', formatsize(self)
##        )
        nDimensions = selfDimensions;
      endif

      % Checking that the indexing information is inside the bounds.
      for i = 1:nDimensions
        indexingInfo = s(1).subs{i};
        % ":" can't be compared and can't be out of bounds
        if ~isequal(indexingInfo, ":")
          assert(
            all(
              indexingInfo >= 1 & indexingInfo <= length(op1.indexSets{i})
            ),
            'Index is out of bounds.'
          )
        endif
        % Remaining sets after indexing.
        indexSets{i} = op1.indexSets{i}(indexingInfo);
        % Indexing information expanded to account for blocks.
        blockS(1).subs{i} = [op1.indexBlocks{i}{indexingInfo}];
      endfor
      
      self = MultiDimVar(
        op1.indexLabels,
        indexSets,
        builtin('subsref', op1.value, blockS)
      );
      % To access to properties of the subscripted object.
      if length(s) > 1
        s = s(2:end);
        self = subsref(self, s);
      endif
    case '.'
      self = builtin('subsref', op1, s);
    case '{}'
      self = builtin('subsref', op1, s);
    otherwise
      error('Not a valid indexing expression')
  endswitch
endfunction