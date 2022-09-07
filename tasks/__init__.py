"""

@author : "PREISIG, Heinz A"
@copyright : "Copyright 2015, PREISIG, Heinz A" 
"""

__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2017. 03. 22"
__license__ = "generic module"
__version__ = "0"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"



import os
import sys

root = os.path.abspath(os.path.join(".."))
emmo = "/home/heinz/1_Gits/EMMO-python/emmo/"
sys.path.extend([root, os.path.join(root, 'packages'), os.path.join(root, 'tasks'), emmo])
