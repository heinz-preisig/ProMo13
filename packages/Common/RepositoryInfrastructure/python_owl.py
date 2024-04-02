

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

ontology = OntologyContainer("processes_starter") #'flash_03')


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

# V_12
label = variables[V_12]["label"]
network = variables[V_12]["network"]
variable_type = variables[V_12]["type"]
label = variables[V_12]["label"]
doc = variables[V_12]["doc"]
onto_ID = "V_V_12"
V_V_12 = onto.ProMoVar( onto_ID )
V_V_12.label = label
V_V_12.network = network
V_V_12.variable_type = variable_type
V_V_12.comment = doc

units = variables[V_12]["units"].asList()
V_V_12.time = [ units[0] ]
V_V_12.length = [ units[1] ]
V_V_12.amount = [ units[2] ]
V_V_12.mass = [ units[3] ]
V_V_12.temperature = [ units[4] ]
V_V_12.current = [ units[5] ]
V_V_12.light = [ units[6] ]

# V_13
label = variables[V_13]["label"]
network = variables[V_13]["network"]
variable_type = variables[V_13]["type"]
label = variables[V_13]["label"]
doc = variables[V_13]["doc"]
onto_ID = "V_V_13"
V_V_13 = onto.ProMoVar( onto_ID )
V_V_13.label = label
V_V_13.network = network
V_V_13.variable_type = variable_type
V_V_13.comment = doc

units = variables[V_13]["units"].asList()
V_V_13.time = [ units[0] ]
V_V_13.length = [ units[1] ]
V_V_13.amount = [ units[2] ]
V_V_13.mass = [ units[3] ]
V_V_13.temperature = [ units[4] ]
V_V_13.current = [ units[5] ]
V_V_13.light = [ units[6] ]

# V_14
label = variables[V_14]["label"]
network = variables[V_14]["network"]
variable_type = variables[V_14]["type"]
label = variables[V_14]["label"]
doc = variables[V_14]["doc"]
onto_ID = "V_V_14"
V_V_14 = onto.ProMoVar( onto_ID )
V_V_14.label = label
V_V_14.network = network
V_V_14.variable_type = variable_type
V_V_14.comment = doc

units = variables[V_14]["units"].asList()
V_V_14.time = [ units[0] ]
V_V_14.length = [ units[1] ]
V_V_14.amount = [ units[2] ]
V_V_14.mass = [ units[3] ]
V_V_14.temperature = [ units[4] ]
V_V_14.current = [ units[5] ]
V_V_14.light = [ units[6] ]

# V_15
label = variables[V_15]["label"]
network = variables[V_15]["network"]
variable_type = variables[V_15]["type"]
label = variables[V_15]["label"]
doc = variables[V_15]["doc"]
onto_ID = "V_V_15"
V_V_15 = onto.ProMoVar( onto_ID )
V_V_15.label = label
V_V_15.network = network
V_V_15.variable_type = variable_type
V_V_15.comment = doc

units = variables[V_15]["units"].asList()
V_V_15.time = [ units[0] ]
V_V_15.length = [ units[1] ]
V_V_15.amount = [ units[2] ]
V_V_15.mass = [ units[3] ]
V_V_15.temperature = [ units[4] ]
V_V_15.current = [ units[5] ]
V_V_15.light = [ units[6] ]

# V_16
label = variables[V_16]["label"]
network = variables[V_16]["network"]
variable_type = variables[V_16]["type"]
label = variables[V_16]["label"]
doc = variables[V_16]["doc"]
onto_ID = "V_V_16"
V_V_16 = onto.ProMoVar( onto_ID )
V_V_16.label = label
V_V_16.network = network
V_V_16.variable_type = variable_type
V_V_16.comment = doc

units = variables[V_16]["units"].asList()
V_V_16.time = [ units[0] ]
V_V_16.length = [ units[1] ]
V_V_16.amount = [ units[2] ]
V_V_16.mass = [ units[3] ]
V_V_16.temperature = [ units[4] ]
V_V_16.current = [ units[5] ]
V_V_16.light = [ units[6] ]

# V_17
label = variables[V_17]["label"]
network = variables[V_17]["network"]
variable_type = variables[V_17]["type"]
label = variables[V_17]["label"]
doc = variables[V_17]["doc"]
onto_ID = "V_V_17"
V_V_17 = onto.ProMoVar( onto_ID )
V_V_17.label = label
V_V_17.network = network
V_V_17.variable_type = variable_type
V_V_17.comment = doc

units = variables[V_17]["units"].asList()
V_V_17.time = [ units[0] ]
V_V_17.length = [ units[1] ]
V_V_17.amount = [ units[2] ]
V_V_17.mass = [ units[3] ]
V_V_17.temperature = [ units[4] ]
V_V_17.current = [ units[5] ]
V_V_17.light = [ units[6] ]

# V_18
label = variables[V_18]["label"]
network = variables[V_18]["network"]
variable_type = variables[V_18]["type"]
label = variables[V_18]["label"]
doc = variables[V_18]["doc"]
onto_ID = "V_V_18"
V_V_18 = onto.ProMoVar( onto_ID )
V_V_18.label = label
V_V_18.network = network
V_V_18.variable_type = variable_type
V_V_18.comment = doc

units = variables[V_18]["units"].asList()
V_V_18.time = [ units[0] ]
V_V_18.length = [ units[1] ]
V_V_18.amount = [ units[2] ]
V_V_18.mass = [ units[3] ]
V_V_18.temperature = [ units[4] ]
V_V_18.current = [ units[5] ]
V_V_18.light = [ units[6] ]

# V_19
label = variables[V_19]["label"]
network = variables[V_19]["network"]
variable_type = variables[V_19]["type"]
label = variables[V_19]["label"]
doc = variables[V_19]["doc"]
onto_ID = "V_V_19"
V_V_19 = onto.ProMoVar( onto_ID )
V_V_19.label = label
V_V_19.network = network
V_V_19.variable_type = variable_type
V_V_19.comment = doc

units = variables[V_19]["units"].asList()
V_V_19.time = [ units[0] ]
V_V_19.length = [ units[1] ]
V_V_19.amount = [ units[2] ]
V_V_19.mass = [ units[3] ]
V_V_19.temperature = [ units[4] ]
V_V_19.current = [ units[5] ]
V_V_19.light = [ units[6] ]

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

# V_20
label = variables[V_20]["label"]
network = variables[V_20]["network"]
variable_type = variables[V_20]["type"]
label = variables[V_20]["label"]
doc = variables[V_20]["doc"]
onto_ID = "V_V_20"
V_V_20 = onto.ProMoVar( onto_ID )
V_V_20.label = label
V_V_20.network = network
V_V_20.variable_type = variable_type
V_V_20.comment = doc

units = variables[V_20]["units"].asList()
V_V_20.time = [ units[0] ]
V_V_20.length = [ units[1] ]
V_V_20.amount = [ units[2] ]
V_V_20.mass = [ units[3] ]
V_V_20.temperature = [ units[4] ]
V_V_20.current = [ units[5] ]
V_V_20.light = [ units[6] ]

# V_21
label = variables[V_21]["label"]
network = variables[V_21]["network"]
variable_type = variables[V_21]["type"]
label = variables[V_21]["label"]
doc = variables[V_21]["doc"]
onto_ID = "V_V_21"
V_V_21 = onto.ProMoVar( onto_ID )
V_V_21.label = label
V_V_21.network = network
V_V_21.variable_type = variable_type
V_V_21.comment = doc

units = variables[V_21]["units"].asList()
V_V_21.time = [ units[0] ]
V_V_21.length = [ units[1] ]
V_V_21.amount = [ units[2] ]
V_V_21.mass = [ units[3] ]
V_V_21.temperature = [ units[4] ]
V_V_21.current = [ units[5] ]
V_V_21.light = [ units[6] ]

# V_22
label = variables[V_22]["label"]
network = variables[V_22]["network"]
variable_type = variables[V_22]["type"]
label = variables[V_22]["label"]
doc = variables[V_22]["doc"]
onto_ID = "V_V_22"
V_V_22 = onto.ProMoVar( onto_ID )
V_V_22.label = label
V_V_22.network = network
V_V_22.variable_type = variable_type
V_V_22.comment = doc

units = variables[V_22]["units"].asList()
V_V_22.time = [ units[0] ]
V_V_22.length = [ units[1] ]
V_V_22.amount = [ units[2] ]
V_V_22.mass = [ units[3] ]
V_V_22.temperature = [ units[4] ]
V_V_22.current = [ units[5] ]
V_V_22.light = [ units[6] ]

# V_23
label = variables[V_23]["label"]
network = variables[V_23]["network"]
variable_type = variables[V_23]["type"]
label = variables[V_23]["label"]
doc = variables[V_23]["doc"]
onto_ID = "V_V_23"
V_V_23 = onto.ProMoVar( onto_ID )
V_V_23.label = label
V_V_23.network = network
V_V_23.variable_type = variable_type
V_V_23.comment = doc

units = variables[V_23]["units"].asList()
V_V_23.time = [ units[0] ]
V_V_23.length = [ units[1] ]
V_V_23.amount = [ units[2] ]
V_V_23.mass = [ units[3] ]
V_V_23.temperature = [ units[4] ]
V_V_23.current = [ units[5] ]
V_V_23.light = [ units[6] ]

# V_24
label = variables[V_24]["label"]
network = variables[V_24]["network"]
variable_type = variables[V_24]["type"]
label = variables[V_24]["label"]
doc = variables[V_24]["doc"]
onto_ID = "V_V_24"
V_V_24 = onto.ProMoVar( onto_ID )
V_V_24.label = label
V_V_24.network = network
V_V_24.variable_type = variable_type
V_V_24.comment = doc

units = variables[V_24]["units"].asList()
V_V_24.time = [ units[0] ]
V_V_24.length = [ units[1] ]
V_V_24.amount = [ units[2] ]
V_V_24.mass = [ units[3] ]
V_V_24.temperature = [ units[4] ]
V_V_24.current = [ units[5] ]
V_V_24.light = [ units[6] ]

# V_25
label = variables[V_25]["label"]
network = variables[V_25]["network"]
variable_type = variables[V_25]["type"]
label = variables[V_25]["label"]
doc = variables[V_25]["doc"]
onto_ID = "V_V_25"
V_V_25 = onto.ProMoVar( onto_ID )
V_V_25.label = label
V_V_25.network = network
V_V_25.variable_type = variable_type
V_V_25.comment = doc

units = variables[V_25]["units"].asList()
V_V_25.time = [ units[0] ]
V_V_25.length = [ units[1] ]
V_V_25.amount = [ units[2] ]
V_V_25.mass = [ units[3] ]
V_V_25.temperature = [ units[4] ]
V_V_25.current = [ units[5] ]
V_V_25.light = [ units[6] ]

# V_26
label = variables[V_26]["label"]
network = variables[V_26]["network"]
variable_type = variables[V_26]["type"]
label = variables[V_26]["label"]
doc = variables[V_26]["doc"]
onto_ID = "V_V_26"
V_V_26 = onto.ProMoVar( onto_ID )
V_V_26.label = label
V_V_26.network = network
V_V_26.variable_type = variable_type
V_V_26.comment = doc

units = variables[V_26]["units"].asList()
V_V_26.time = [ units[0] ]
V_V_26.length = [ units[1] ]
V_V_26.amount = [ units[2] ]
V_V_26.mass = [ units[3] ]
V_V_26.temperature = [ units[4] ]
V_V_26.current = [ units[5] ]
V_V_26.light = [ units[6] ]

# V_27
label = variables[V_27]["label"]
network = variables[V_27]["network"]
variable_type = variables[V_27]["type"]
label = variables[V_27]["label"]
doc = variables[V_27]["doc"]
onto_ID = "V_V_27"
V_V_27 = onto.ProMoVar( onto_ID )
V_V_27.label = label
V_V_27.network = network
V_V_27.variable_type = variable_type
V_V_27.comment = doc

units = variables[V_27]["units"].asList()
V_V_27.time = [ units[0] ]
V_V_27.length = [ units[1] ]
V_V_27.amount = [ units[2] ]
V_V_27.mass = [ units[3] ]
V_V_27.temperature = [ units[4] ]
V_V_27.current = [ units[5] ]
V_V_27.light = [ units[6] ]

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
#V_12

V_V_12.has_function = []
#V_13

V_V_13.has_function = []
#V_14

V_V_14.has_function = []
#V_15

V_V_15.has_function = []
#V_16

V_V_16.has_function = []
#V_17

V_V_17.has_function = []
#V_18

V_V_18.has_function = []
#V_19

V_V_19.has_function = []
#V_2

V_V_2.has_function = []
#V_20

V_V_20.has_function = []
#V_21

V_V_21.has_function = []
#V_22

V_V_22.has_function = []
#V_23

V_V_23.has_function = []
#V_24

V_V_24.has_function = []
#V_25

V_V_25.has_function = []
#V_26

V_V_26.has_function = []
#V_27

V_V_27.has_function = []
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
