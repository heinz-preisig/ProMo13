function run_tests()
  args = argv();
  folder = 'tests';  % folder containing the test files
  if numel(args) == 0  % if no arguments are provided
    files = readdir(folder);  % get a list of all files in the folder
  else  % if arguments are provided
    files = strcat('test_', args, '.m');  % create file names from the arguments
  end

  nTestsTotal = 0;
  nTestsPassed = 0;
  for ii = 1:numel(files)
    [~, name, ext] = fileparts(files{ii});  % get the file name and extension
    if strcmp(ext, '.m')  % if the file is a .m file
      testName = strrep(name, 'test_', '');  % remove 'test_' prefix
      [n, nmax] = test(fullfile(folder, files{ii}));  % get the number of passed and total tests
      nTestsPassed = nTestsPassed + n;
      nTestsTotal = nTestsTotal + nmax;
      printf("%s\n", repmat('=',1,58));
      printf("Tests for %-40s %3d/%-3d\n", testName, n, nmax);
      if n < nmax  % if any tests failed
        printf("The following tests failed:\n");
        test(fullfile(folder, files{ii}));  % run the tests again to print information about failed tests
      end
    end
  end
  printf("%s\n", repmat('=',1,58));
  printf("%s\n", repmat('=',1,58));
  printf("%-50s %3d/%-3d\n","TOTAL", nTestsPassed, nTestsTotal);
  printf("%s\n", repmat('=',1,58));
  printf("%s\n", repmat('=',1,58));
end
