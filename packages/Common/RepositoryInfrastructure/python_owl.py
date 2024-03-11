

#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Ontology design facility
===============================================================================

This program is part of the ProcessModelling suite

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "16.09.2019"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "5.04"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"


import sys
import os

ProMo_path = os.path.join("../../","ProMo")



root = os.path.abspath(ProMo_path)      #os.path.join("../../"{{ProMo}}) #ProcessModeller_v7_04"))

ext = [root, os.path.join(root, 'packages'), \
             os.path.join(root, 'tasks'), \
             os.path.join(root, 'packages', 'OntologyBuilder', 'EMMO_Integration')
       ]
# print(os.path.join(root, 'packages', 'OntologyBuilder', 'EMMO_Integration'))

# emmo = "/home/heinz/1_Gits/ProcessModeller/ProcessModeller_v7_04/packages/OntologyBuilder/EMMO_Integration/"

sys.path.extend(ext)
from OntologyBuilder.EMMO_Integration.emmo_attach import ProMoOwlOntology
from Common.ontology_container import OntologyContainer

from owlready2 import *

ontology = OntologyContainer("Sandbox21") #'flash_03')


variables = ontology.variables

name = "play"
owlfile = name+".owl"

# onto  = O.setup_ontology(name)
o = ProMoOwlOntology()
onto = o.setupOnto()

with onto:
  class ProMoVar(onto.VAR):
    pass

  class has_function(ObjectProperty):
    domain = [ProMoVar]
    range  = [ProMoVar]
    pass

  class function(Thing):
    domain  = [ProMoVar]
    range   = [ProMoVar]
    pass

  class is_function_of(ObjectProperty):
    domain = [ProMoVar]
    range  = [ProMoVar]
    pass

# V_1
label = variables[V_1]["label"]
network = variables[V_1]["network"]
variable_type = variables[V_1]["type"]
label = variables[V_1]["label"]
doc = variables[V_1]["doc"]
onto_ID = "V_V_1"
V_V_1 = onto.ProMoVar( onto_ID )
V_V_1.label = label
V_V_1.network = network
V_V_1.variable_type = variable_type
V_V_1.comment = doc

units = variables[V_1]["units"].asList()
V_V_1.time = [ units[0] ]
V_V_1.length = [ units[1] ]
V_V_1.amount = [ units[2] ]
V_V_1.mass = [ units[3] ]
V_V_1.temperature = [ units[4] ]
V_V_1.current = [ units[5] ]
V_V_1.light = [ units[6] ]

# V_10
label = variables[V_10]["label"]
network = variables[V_10]["network"]
variable_type = variables[V_10]["type"]
label = variables[V_10]["label"]
doc = variables[V_10]["doc"]
onto_ID = "V_V_10"
V_V_10 = onto.ProMoVar( onto_ID )
V_V_10.label = label
V_V_10.network = network
V_V_10.variable_type = variable_type
V_V_10.comment = doc

units = variables[V_10]["units"].asList()
V_V_10.time = [ units[0] ]
V_V_10.length = [ units[1] ]
V_V_10.amount = [ units[2] ]
V_V_10.mass = [ units[3] ]
V_V_10.temperature = [ units[4] ]
V_V_10.current = [ units[5] ]
V_V_10.light = [ units[6] ]

# V_11
label = variables[V_11]["label"]
network = variables[V_11]["network"]
variable_type = variables[V_11]["type"]
label = variables[V_11]["label"]
doc = variables[V_11]["doc"]
onto_ID = "V_V_11"
V_V_11 = onto.ProMoVar( onto_ID )
V_V_11.label = label
V_V_11.network = network
V_V_11.variable_type = variable_type
V_V_11.comment = doc

units = variables[V_11]["units"].asList()
V_V_11.time = [ units[0] ]
V_V_11.length = [ units[1] ]
V_V_11.amount = [ units[2] ]
V_V_11.mass = [ units[3] ]
V_V_11.temperature = [ units[4] ]
V_V_11.current = [ units[5] ]
V_V_11.light = [ units[6] ]

# V_2
label = variables[V_2]["label"]
network = variables[V_2]["network"]
variable_type = variables[V_2]["type"]
label = variables[V_2]["label"]
doc = variables[V_2]["doc"]
onto_ID = "V_V_2"
V_V_2 = onto.ProMoVar( onto_ID )
V_V_2.label = label
V_V_2.network = network
V_V_2.variable_type = variable_type
V_V_2.comment = doc

units = variables[V_2]["units"].asList()
V_V_2.time = [ units[0] ]
V_V_2.length = [ units[1] ]
V_V_2.amount = [ units[2] ]
V_V_2.mass = [ units[3] ]
V_V_2.temperature = [ units[4] ]
V_V_2.current = [ units[5] ]
V_V_2.light = [ units[6] ]

# V_3
label = variables[V_3]["label"]
network = variables[V_3]["network"]
variable_type = variables[V_3]["type"]
label = variables[V_3]["label"]
doc = variables[V_3]["doc"]
onto_ID = "V_V_3"
V_V_3 = onto.ProMoVar( onto_ID )
V_V_3.label = label
V_V_3.network = network
V_V_3.variable_type = variable_type
V_V_3.comment = doc

units = variables[V_3]["units"].asList()
V_V_3.time = [ units[0] ]
V_V_3.length = [ units[1] ]
V_V_3.amount = [ units[2] ]
V_V_3.mass = [ units[3] ]
V_V_3.temperature = [ units[4] ]
V_V_3.current = [ units[5] ]
V_V_3.light = [ units[6] ]

# V_4
label = variables[V_4]["label"]
network = variables[V_4]["network"]
variable_type = variables[V_4]["type"]
label = variables[V_4]["label"]
doc = variables[V_4]["doc"]
onto_ID = "V_V_4"
V_V_4 = onto.ProMoVar( onto_ID )
V_V_4.label = label
V_V_4.network = network
V_V_4.variable_type = variable_type
V_V_4.comment = doc

units = variables[V_4]["units"].asList()
V_V_4.time = [ units[0] ]
V_V_4.length = [ units[1] ]
V_V_4.amount = [ units[2] ]
V_V_4.mass = [ units[3] ]
V_V_4.temperature = [ units[4] ]
V_V_4.current = [ units[5] ]
V_V_4.light = [ units[6] ]

# V_5
label = variables[V_5]["label"]
network = variables[V_5]["network"]
variable_type = variables[V_5]["type"]
label = variables[V_5]["label"]
doc = variables[V_5]["doc"]
onto_ID = "V_V_5"
V_V_5 = onto.ProMoVar( onto_ID )
V_V_5.label = label
V_V_5.network = network
V_V_5.variable_type = variable_type
V_V_5.comment = doc

units = variables[V_5]["units"].asList()
V_V_5.time = [ units[0] ]
V_V_5.length = [ units[1] ]
V_V_5.amount = [ units[2] ]
V_V_5.mass = [ units[3] ]
V_V_5.temperature = [ units[4] ]
V_V_5.current = [ units[5] ]
V_V_5.light = [ units[6] ]

# V_6
label = variables[V_6]["label"]
network = variables[V_6]["network"]
variable_type = variables[V_6]["type"]
label = variables[V_6]["label"]
doc = variables[V_6]["doc"]
onto_ID = "V_V_6"
V_V_6 = onto.ProMoVar( onto_ID )
V_V_6.label = label
V_V_6.network = network
V_V_6.variable_type = variable_type
V_V_6.comment = doc

units = variables[V_6]["units"].asList()
V_V_6.time = [ units[0] ]
V_V_6.length = [ units[1] ]
V_V_6.amount = [ units[2] ]
V_V_6.mass = [ units[3] ]
V_V_6.temperature = [ units[4] ]
V_V_6.current = [ units[5] ]
V_V_6.light = [ units[6] ]

# V_7
label = variables[V_7]["label"]
network = variables[V_7]["network"]
variable_type = variables[V_7]["type"]
label = variables[V_7]["label"]
doc = variables[V_7]["doc"]
onto_ID = "V_V_7"
V_V_7 = onto.ProMoVar( onto_ID )
V_V_7.label = label
V_V_7.network = network
V_V_7.variable_type = variable_type
V_V_7.comment = doc

units = variables[V_7]["units"].asList()
V_V_7.time = [ units[0] ]
V_V_7.length = [ units[1] ]
V_V_7.amount = [ units[2] ]
V_V_7.mass = [ units[3] ]
V_V_7.temperature = [ units[4] ]
V_V_7.current = [ units[5] ]
V_V_7.light = [ units[6] ]

# V_8
label = variables[V_8]["label"]
network = variables[V_8]["network"]
variable_type = variables[V_8]["type"]
label = variables[V_8]["label"]
doc = variables[V_8]["doc"]
onto_ID = "V_V_8"
V_V_8 = onto.ProMoVar( onto_ID )
V_V_8.label = label
V_V_8.network = network
V_V_8.variable_type = variable_type
V_V_8.comment = doc

units = variables[V_8]["units"].asList()
V_V_8.time = [ units[0] ]
V_V_8.length = [ units[1] ]
V_V_8.amount = [ units[2] ]
V_V_8.mass = [ units[3] ]
V_V_8.temperature = [ units[4] ]
V_V_8.current = [ units[5] ]
V_V_8.light = [ units[6] ]

# V_9
label = variables[V_9]["label"]
network = variables[V_9]["network"]
variable_type = variables[V_9]["type"]
label = variables[V_9]["label"]
doc = variables[V_9]["doc"]
onto_ID = "V_V_9"
V_V_9 = onto.ProMoVar( onto_ID )
V_V_9.label = label
V_V_9.network = network
V_V_9.variable_type = variable_type
V_V_9.comment = doc

units = variables[V_9]["units"].asList()
V_V_9.time = [ units[0] ]
V_V_9.length = [ units[1] ]
V_V_9.amount = [ units[2] ]
V_V_9.mass = [ units[3] ]
V_V_9.temperature = [ units[4] ]
V_V_9.current = [ units[5] ]
V_V_9.light = [ units[6] ]

# functions assignments

#V_1

V_V_1.has_function = []
#V_10

V_V_10.has_function = []
#V_11

V_V_11.has_function = []
#V_2

V_V_2.has_function = []
#V_3

V_V_3.has_function = []
#V_4

V_V_4.has_function = []
#V_5

V_V_5.has_function = []
#V_6

V_V_6.has_function = []
#V_7

V_V_7.has_function = []
#V_8

V_V_8.has_function = []
#V_9

V_V_9.has_function = []

onto.save("variables.owl")
