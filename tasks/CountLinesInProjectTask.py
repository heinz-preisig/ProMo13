#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Count the number of code lines in the project
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2014. 08. 09"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import glob
import os

if __name__ == '__main__':

  line_counter = 0
  file_counter = 0
  root = "."
  root = os.getcwd()

  py_files = []
  txt_file = 'countfile.txt'
  with open(txt_file, 'w') as out:
    for (dirpath, dirnames, filenames) in os.walk(root):
      for file_name in filenames:
        if ".py" in file_name:
          if not(".pyc" in file_name):
            next_name = os.path.join(dirpath,file_name)
            # print(next_name)
            py_files.append(next_name)

    for file_name in py_files:
      file_counter += 1
      with open(file_name, 'r') as f:
        count = sum(1 for line in f)
        line_counter += count
        out.write('{c} \t {f}\n'.format(c=count, f=file_name))


  print("\n total number of files : %s" % file_counter)
  print("\n total number of lines : %s" % line_counter)