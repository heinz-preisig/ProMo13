#!/usr/bin/python3.5
# encoding: utf-8

"""

@author : "PREISIG, Heinz A"
@copyright : "Copyright 2015, PREISIG, Heinz A" 
"""

__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2017. 03. 23"
__license__ = "generic module"
__version__ = "0"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

# ===============================================================================
# Main
# ===============================================================================

import Common.automata.automata_modeller as A
import Common.common_resources as CR

if __name__ == '__main__':
  mouse_automaton = A.MOUSE_AUTOMATON
  key_automaton = A.KEY_AUTOMATON
  designated_automaton = A.DESIGNATED_KEYS

  data = {}
  data["MOUSE_AUTOMATON"] = mouse_automaton
  data["KEY_AUTOMATON"] = key_automaton
  data["DESIGNATED_KEYS"] = designated_automaton

  CR.putData(data, 'autoconvert.json', indent=2)
