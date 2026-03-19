

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
# from OntologyBuilder.EMMO_Integration.emmo_attach import ProMoOwlOntology
from OntologyBuilder.Attic_OntologyEquationAssignmentEditor.EMMO_Integration.emmo_attach import ProMoOwlOntology
from Common.exchange_board import ProMoExchangeBoard

from owlready2 import *

ontology = ProMoExchangeBoard("ProMo_sandbox8_") #'flash_03')


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

# 1
label = variables[1]["label"]
network = variables[1]["network"]
variable_type = variables[1]["type"]
label = variables[1]["label"]
doc = variables[1]["doc"]
onto_ID = "V_1"
V_1 = onto.ProMoVar( onto_ID )
V_1.label = label
V_1.network = network
V_1.variable_type = variable_type
V_1.comment = doc

units = variables[1]["units"].asList()
V_1.time = [ units[0] ]
V_1.length = [ units[1] ]
V_1.amount = [ units[2] ]
V_1.mass = [ units[3] ]
V_1.temperature = [ units[4] ]
V_1.current = [ units[5] ]
V_1.light = [ units[6] ]

# 2
label = variables[2]["label"]
network = variables[2]["network"]
variable_type = variables[2]["type"]
label = variables[2]["label"]
doc = variables[2]["doc"]
onto_ID = "V_2"
V_2 = onto.ProMoVar( onto_ID )
V_2.label = label
V_2.network = network
V_2.variable_type = variable_type
V_2.comment = doc

units = variables[2]["units"].asList()
V_2.time = [ units[0] ]
V_2.length = [ units[1] ]
V_2.amount = [ units[2] ]
V_2.mass = [ units[3] ]
V_2.temperature = [ units[4] ]
V_2.current = [ units[5] ]
V_2.light = [ units[6] ]

# 3
label = variables[3]["label"]
network = variables[3]["network"]
variable_type = variables[3]["type"]
label = variables[3]["label"]
doc = variables[3]["doc"]
onto_ID = "V_3"
V_3 = onto.ProMoVar( onto_ID )
V_3.label = label
V_3.network = network
V_3.variable_type = variable_type
V_3.comment = doc

units = variables[3]["units"].asList()
V_3.time = [ units[0] ]
V_3.length = [ units[1] ]
V_3.amount = [ units[2] ]
V_3.mass = [ units[3] ]
V_3.temperature = [ units[4] ]
V_3.current = [ units[5] ]
V_3.light = [ units[6] ]

# 4
label = variables[4]["label"]
network = variables[4]["network"]
variable_type = variables[4]["type"]
label = variables[4]["label"]
doc = variables[4]["doc"]
onto_ID = "V_4"
V_4 = onto.ProMoVar( onto_ID )
V_4.label = label
V_4.network = network
V_4.variable_type = variable_type
V_4.comment = doc

units = variables[4]["units"].asList()
V_4.time = [ units[0] ]
V_4.length = [ units[1] ]
V_4.amount = [ units[2] ]
V_4.mass = [ units[3] ]
V_4.temperature = [ units[4] ]
V_4.current = [ units[5] ]
V_4.light = [ units[6] ]

# 5
label = variables[5]["label"]
network = variables[5]["network"]
variable_type = variables[5]["type"]
label = variables[5]["label"]
doc = variables[5]["doc"]
onto_ID = "V_5"
V_5 = onto.ProMoVar( onto_ID )
V_5.label = label
V_5.network = network
V_5.variable_type = variable_type
V_5.comment = doc

units = variables[5]["units"].asList()
V_5.time = [ units[0] ]
V_5.length = [ units[1] ]
V_5.amount = [ units[2] ]
V_5.mass = [ units[3] ]
V_5.temperature = [ units[4] ]
V_5.current = [ units[5] ]
V_5.light = [ units[6] ]

# 6
label = variables[6]["label"]
network = variables[6]["network"]
variable_type = variables[6]["type"]
label = variables[6]["label"]
doc = variables[6]["doc"]
onto_ID = "V_6"
V_6 = onto.ProMoVar( onto_ID )
V_6.label = label
V_6.network = network
V_6.variable_type = variable_type
V_6.comment = doc

units = variables[6]["units"].asList()
V_6.time = [ units[0] ]
V_6.length = [ units[1] ]
V_6.amount = [ units[2] ]
V_6.mass = [ units[3] ]
V_6.temperature = [ units[4] ]
V_6.current = [ units[5] ]
V_6.light = [ units[6] ]

# 7
label = variables[7]["label"]
network = variables[7]["network"]
variable_type = variables[7]["type"]
label = variables[7]["label"]
doc = variables[7]["doc"]
onto_ID = "V_7"
V_7 = onto.ProMoVar( onto_ID )
V_7.label = label
V_7.network = network
V_7.variable_type = variable_type
V_7.comment = doc

units = variables[7]["units"].asList()
V_7.time = [ units[0] ]
V_7.length = [ units[1] ]
V_7.amount = [ units[2] ]
V_7.mass = [ units[3] ]
V_7.temperature = [ units[4] ]
V_7.current = [ units[5] ]
V_7.light = [ units[6] ]

# 8
label = variables[8]["label"]
network = variables[8]["network"]
variable_type = variables[8]["type"]
label = variables[8]["label"]
doc = variables[8]["doc"]
onto_ID = "V_8"
V_8 = onto.ProMoVar( onto_ID )
V_8.label = label
V_8.network = network
V_8.variable_type = variable_type
V_8.comment = doc

units = variables[8]["units"].asList()
V_8.time = [ units[0] ]
V_8.length = [ units[1] ]
V_8.amount = [ units[2] ]
V_8.mass = [ units[3] ]
V_8.temperature = [ units[4] ]
V_8.current = [ units[5] ]
V_8.light = [ units[6] ]

# 9
label = variables[9]["label"]
network = variables[9]["network"]
variable_type = variables[9]["type"]
label = variables[9]["label"]
doc = variables[9]["doc"]
onto_ID = "V_9"
V_9 = onto.ProMoVar( onto_ID )
V_9.label = label
V_9.network = network
V_9.variable_type = variable_type
V_9.comment = doc

units = variables[9]["units"].asList()
V_9.time = [ units[0] ]
V_9.length = [ units[1] ]
V_9.amount = [ units[2] ]
V_9.mass = [ units[3] ]
V_9.temperature = [ units[4] ]
V_9.current = [ units[5] ]
V_9.light = [ units[6] ]

# 10
label = variables[10]["label"]
network = variables[10]["network"]
variable_type = variables[10]["type"]
label = variables[10]["label"]
doc = variables[10]["doc"]
onto_ID = "V_10"
V_10 = onto.ProMoVar( onto_ID )
V_10.label = label
V_10.network = network
V_10.variable_type = variable_type
V_10.comment = doc

units = variables[10]["units"].asList()
V_10.time = [ units[0] ]
V_10.length = [ units[1] ]
V_10.amount = [ units[2] ]
V_10.mass = [ units[3] ]
V_10.temperature = [ units[4] ]
V_10.current = [ units[5] ]
V_10.light = [ units[6] ]

# 11
label = variables[11]["label"]
network = variables[11]["network"]
variable_type = variables[11]["type"]
label = variables[11]["label"]
doc = variables[11]["doc"]
onto_ID = "V_11"
V_11 = onto.ProMoVar( onto_ID )
V_11.label = label
V_11.network = network
V_11.variable_type = variable_type
V_11.comment = doc

units = variables[11]["units"].asList()
V_11.time = [ units[0] ]
V_11.length = [ units[1] ]
V_11.amount = [ units[2] ]
V_11.mass = [ units[3] ]
V_11.temperature = [ units[4] ]
V_11.current = [ units[5] ]
V_11.light = [ units[6] ]

# 12
label = variables[12]["label"]
network = variables[12]["network"]
variable_type = variables[12]["type"]
label = variables[12]["label"]
doc = variables[12]["doc"]
onto_ID = "V_12"
V_12 = onto.ProMoVar( onto_ID )
V_12.label = label
V_12.network = network
V_12.variable_type = variable_type
V_12.comment = doc

units = variables[12]["units"].asList()
V_12.time = [ units[0] ]
V_12.length = [ units[1] ]
V_12.amount = [ units[2] ]
V_12.mass = [ units[3] ]
V_12.temperature = [ units[4] ]
V_12.current = [ units[5] ]
V_12.light = [ units[6] ]

# 13
label = variables[13]["label"]
network = variables[13]["network"]
variable_type = variables[13]["type"]
label = variables[13]["label"]
doc = variables[13]["doc"]
onto_ID = "V_13"
V_13 = onto.ProMoVar( onto_ID )
V_13.label = label
V_13.network = network
V_13.variable_type = variable_type
V_13.comment = doc

units = variables[13]["units"].asList()
V_13.time = [ units[0] ]
V_13.length = [ units[1] ]
V_13.amount = [ units[2] ]
V_13.mass = [ units[3] ]
V_13.temperature = [ units[4] ]
V_13.current = [ units[5] ]
V_13.light = [ units[6] ]

# 14
label = variables[14]["label"]
network = variables[14]["network"]
variable_type = variables[14]["type"]
label = variables[14]["label"]
doc = variables[14]["doc"]
onto_ID = "V_14"
V_14 = onto.ProMoVar( onto_ID )
V_14.label = label
V_14.network = network
V_14.variable_type = variable_type
V_14.comment = doc

units = variables[14]["units"].asList()
V_14.time = [ units[0] ]
V_14.length = [ units[1] ]
V_14.amount = [ units[2] ]
V_14.mass = [ units[3] ]
V_14.temperature = [ units[4] ]
V_14.current = [ units[5] ]
V_14.light = [ units[6] ]

# 15
label = variables[15]["label"]
network = variables[15]["network"]
variable_type = variables[15]["type"]
label = variables[15]["label"]
doc = variables[15]["doc"]
onto_ID = "V_15"
V_15 = onto.ProMoVar( onto_ID )
V_15.label = label
V_15.network = network
V_15.variable_type = variable_type
V_15.comment = doc

units = variables[15]["units"].asList()
V_15.time = [ units[0] ]
V_15.length = [ units[1] ]
V_15.amount = [ units[2] ]
V_15.mass = [ units[3] ]
V_15.temperature = [ units[4] ]
V_15.current = [ units[5] ]
V_15.light = [ units[6] ]

# 16
label = variables[16]["label"]
network = variables[16]["network"]
variable_type = variables[16]["type"]
label = variables[16]["label"]
doc = variables[16]["doc"]
onto_ID = "V_16"
V_16 = onto.ProMoVar( onto_ID )
V_16.label = label
V_16.network = network
V_16.variable_type = variable_type
V_16.comment = doc

units = variables[16]["units"].asList()
V_16.time = [ units[0] ]
V_16.length = [ units[1] ]
V_16.amount = [ units[2] ]
V_16.mass = [ units[3] ]
V_16.temperature = [ units[4] ]
V_16.current = [ units[5] ]
V_16.light = [ units[6] ]

# 17
label = variables[17]["label"]
network = variables[17]["network"]
variable_type = variables[17]["type"]
label = variables[17]["label"]
doc = variables[17]["doc"]
onto_ID = "V_17"
V_17 = onto.ProMoVar( onto_ID )
V_17.label = label
V_17.network = network
V_17.variable_type = variable_type
V_17.comment = doc

units = variables[17]["units"].asList()
V_17.time = [ units[0] ]
V_17.length = [ units[1] ]
V_17.amount = [ units[2] ]
V_17.mass = [ units[3] ]
V_17.temperature = [ units[4] ]
V_17.current = [ units[5] ]
V_17.light = [ units[6] ]

# 18
label = variables[18]["label"]
network = variables[18]["network"]
variable_type = variables[18]["type"]
label = variables[18]["label"]
doc = variables[18]["doc"]
onto_ID = "V_18"
V_18 = onto.ProMoVar( onto_ID )
V_18.label = label
V_18.network = network
V_18.variable_type = variable_type
V_18.comment = doc

units = variables[18]["units"].asList()
V_18.time = [ units[0] ]
V_18.length = [ units[1] ]
V_18.amount = [ units[2] ]
V_18.mass = [ units[3] ]
V_18.temperature = [ units[4] ]
V_18.current = [ units[5] ]
V_18.light = [ units[6] ]

# 19
label = variables[19]["label"]
network = variables[19]["network"]
variable_type = variables[19]["type"]
label = variables[19]["label"]
doc = variables[19]["doc"]
onto_ID = "V_19"
V_19 = onto.ProMoVar( onto_ID )
V_19.label = label
V_19.network = network
V_19.variable_type = variable_type
V_19.comment = doc

units = variables[19]["units"].asList()
V_19.time = [ units[0] ]
V_19.length = [ units[1] ]
V_19.amount = [ units[2] ]
V_19.mass = [ units[3] ]
V_19.temperature = [ units[4] ]
V_19.current = [ units[5] ]
V_19.light = [ units[6] ]

# 20
label = variables[20]["label"]
network = variables[20]["network"]
variable_type = variables[20]["type"]
label = variables[20]["label"]
doc = variables[20]["doc"]
onto_ID = "V_20"
V_20 = onto.ProMoVar( onto_ID )
V_20.label = label
V_20.network = network
V_20.variable_type = variable_type
V_20.comment = doc

units = variables[20]["units"].asList()
V_20.time = [ units[0] ]
V_20.length = [ units[1] ]
V_20.amount = [ units[2] ]
V_20.mass = [ units[3] ]
V_20.temperature = [ units[4] ]
V_20.current = [ units[5] ]
V_20.light = [ units[6] ]

# 21
label = variables[21]["label"]
network = variables[21]["network"]
variable_type = variables[21]["type"]
label = variables[21]["label"]
doc = variables[21]["doc"]
onto_ID = "V_21"
V_21 = onto.ProMoVar( onto_ID )
V_21.label = label
V_21.network = network
V_21.variable_type = variable_type
V_21.comment = doc

units = variables[21]["units"].asList()
V_21.time = [ units[0] ]
V_21.length = [ units[1] ]
V_21.amount = [ units[2] ]
V_21.mass = [ units[3] ]
V_21.temperature = [ units[4] ]
V_21.current = [ units[5] ]
V_21.light = [ units[6] ]

# 22
label = variables[22]["label"]
network = variables[22]["network"]
variable_type = variables[22]["type"]
label = variables[22]["label"]
doc = variables[22]["doc"]
onto_ID = "V_22"
V_22 = onto.ProMoVar( onto_ID )
V_22.label = label
V_22.network = network
V_22.variable_type = variable_type
V_22.comment = doc

units = variables[22]["units"].asList()
V_22.time = [ units[0] ]
V_22.length = [ units[1] ]
V_22.amount = [ units[2] ]
V_22.mass = [ units[3] ]
V_22.temperature = [ units[4] ]
V_22.current = [ units[5] ]
V_22.light = [ units[6] ]

# 23
label = variables[23]["label"]
network = variables[23]["network"]
variable_type = variables[23]["type"]
label = variables[23]["label"]
doc = variables[23]["doc"]
onto_ID = "V_23"
V_23 = onto.ProMoVar( onto_ID )
V_23.label = label
V_23.network = network
V_23.variable_type = variable_type
V_23.comment = doc

units = variables[23]["units"].asList()
V_23.time = [ units[0] ]
V_23.length = [ units[1] ]
V_23.amount = [ units[2] ]
V_23.mass = [ units[3] ]
V_23.temperature = [ units[4] ]
V_23.current = [ units[5] ]
V_23.light = [ units[6] ]

# 24
label = variables[24]["label"]
network = variables[24]["network"]
variable_type = variables[24]["type"]
label = variables[24]["label"]
doc = variables[24]["doc"]
onto_ID = "V_24"
V_24 = onto.ProMoVar( onto_ID )
V_24.label = label
V_24.network = network
V_24.variable_type = variable_type
V_24.comment = doc

units = variables[24]["units"].asList()
V_24.time = [ units[0] ]
V_24.length = [ units[1] ]
V_24.amount = [ units[2] ]
V_24.mass = [ units[3] ]
V_24.temperature = [ units[4] ]
V_24.current = [ units[5] ]
V_24.light = [ units[6] ]

# 27
label = variables[27]["label"]
network = variables[27]["network"]
variable_type = variables[27]["type"]
label = variables[27]["label"]
doc = variables[27]["doc"]
onto_ID = "V_27"
V_27 = onto.ProMoVar( onto_ID )
V_27.label = label
V_27.network = network
V_27.variable_type = variable_type
V_27.comment = doc

units = variables[27]["units"].asList()
V_27.time = [ units[0] ]
V_27.length = [ units[1] ]
V_27.amount = [ units[2] ]
V_27.mass = [ units[3] ]
V_27.temperature = [ units[4] ]
V_27.current = [ units[5] ]
V_27.light = [ units[6] ]

# 28
label = variables[28]["label"]
network = variables[28]["network"]
variable_type = variables[28]["type"]
label = variables[28]["label"]
doc = variables[28]["doc"]
onto_ID = "V_28"
V_28 = onto.ProMoVar( onto_ID )
V_28.label = label
V_28.network = network
V_28.variable_type = variable_type
V_28.comment = doc

units = variables[28]["units"].asList()
V_28.time = [ units[0] ]
V_28.length = [ units[1] ]
V_28.amount = [ units[2] ]
V_28.mass = [ units[3] ]
V_28.temperature = [ units[4] ]
V_28.current = [ units[5] ]
V_28.light = [ units[6] ]

# 29
label = variables[29]["label"]
network = variables[29]["network"]
variable_type = variables[29]["type"]
label = variables[29]["label"]
doc = variables[29]["doc"]
onto_ID = "V_29"
V_29 = onto.ProMoVar( onto_ID )
V_29.label = label
V_29.network = network
V_29.variable_type = variable_type
V_29.comment = doc

units = variables[29]["units"].asList()
V_29.time = [ units[0] ]
V_29.length = [ units[1] ]
V_29.amount = [ units[2] ]
V_29.mass = [ units[3] ]
V_29.temperature = [ units[4] ]
V_29.current = [ units[5] ]
V_29.light = [ units[6] ]

# 30
label = variables[30]["label"]
network = variables[30]["network"]
variable_type = variables[30]["type"]
label = variables[30]["label"]
doc = variables[30]["doc"]
onto_ID = "V_30"
V_30 = onto.ProMoVar( onto_ID )
V_30.label = label
V_30.network = network
V_30.variable_type = variable_type
V_30.comment = doc

units = variables[30]["units"].asList()
V_30.time = [ units[0] ]
V_30.length = [ units[1] ]
V_30.amount = [ units[2] ]
V_30.mass = [ units[3] ]
V_30.temperature = [ units[4] ]
V_30.current = [ units[5] ]
V_30.light = [ units[6] ]

# 32
label = variables[32]["label"]
network = variables[32]["network"]
variable_type = variables[32]["type"]
label = variables[32]["label"]
doc = variables[32]["doc"]
onto_ID = "V_32"
V_32 = onto.ProMoVar( onto_ID )
V_32.label = label
V_32.network = network
V_32.variable_type = variable_type
V_32.comment = doc

units = variables[32]["units"].asList()
V_32.time = [ units[0] ]
V_32.length = [ units[1] ]
V_32.amount = [ units[2] ]
V_32.mass = [ units[3] ]
V_32.temperature = [ units[4] ]
V_32.current = [ units[5] ]
V_32.light = [ units[6] ]

# 33
label = variables[33]["label"]
network = variables[33]["network"]
variable_type = variables[33]["type"]
label = variables[33]["label"]
doc = variables[33]["doc"]
onto_ID = "V_33"
V_33 = onto.ProMoVar( onto_ID )
V_33.label = label
V_33.network = network
V_33.variable_type = variable_type
V_33.comment = doc

units = variables[33]["units"].asList()
V_33.time = [ units[0] ]
V_33.length = [ units[1] ]
V_33.amount = [ units[2] ]
V_33.mass = [ units[3] ]
V_33.temperature = [ units[4] ]
V_33.current = [ units[5] ]
V_33.light = [ units[6] ]

# 34
label = variables[34]["label"]
network = variables[34]["network"]
variable_type = variables[34]["type"]
label = variables[34]["label"]
doc = variables[34]["doc"]
onto_ID = "V_34"
V_34 = onto.ProMoVar( onto_ID )
V_34.label = label
V_34.network = network
V_34.variable_type = variable_type
V_34.comment = doc

units = variables[34]["units"].asList()
V_34.time = [ units[0] ]
V_34.length = [ units[1] ]
V_34.amount = [ units[2] ]
V_34.mass = [ units[3] ]
V_34.temperature = [ units[4] ]
V_34.current = [ units[5] ]
V_34.light = [ units[6] ]

# 35
label = variables[35]["label"]
network = variables[35]["network"]
variable_type = variables[35]["type"]
label = variables[35]["label"]
doc = variables[35]["doc"]
onto_ID = "V_35"
V_35 = onto.ProMoVar( onto_ID )
V_35.label = label
V_35.network = network
V_35.variable_type = variable_type
V_35.comment = doc

units = variables[35]["units"].asList()
V_35.time = [ units[0] ]
V_35.length = [ units[1] ]
V_35.amount = [ units[2] ]
V_35.mass = [ units[3] ]
V_35.temperature = [ units[4] ]
V_35.current = [ units[5] ]
V_35.light = [ units[6] ]

# 36
label = variables[36]["label"]
network = variables[36]["network"]
variable_type = variables[36]["type"]
label = variables[36]["label"]
doc = variables[36]["doc"]
onto_ID = "V_36"
V_36 = onto.ProMoVar( onto_ID )
V_36.label = label
V_36.network = network
V_36.variable_type = variable_type
V_36.comment = doc

units = variables[36]["units"].asList()
V_36.time = [ units[0] ]
V_36.length = [ units[1] ]
V_36.amount = [ units[2] ]
V_36.mass = [ units[3] ]
V_36.temperature = [ units[4] ]
V_36.current = [ units[5] ]
V_36.light = [ units[6] ]

# 37
label = variables[37]["label"]
network = variables[37]["network"]
variable_type = variables[37]["type"]
label = variables[37]["label"]
doc = variables[37]["doc"]
onto_ID = "V_37"
V_37 = onto.ProMoVar( onto_ID )
V_37.label = label
V_37.network = network
V_37.variable_type = variable_type
V_37.comment = doc

units = variables[37]["units"].asList()
V_37.time = [ units[0] ]
V_37.length = [ units[1] ]
V_37.amount = [ units[2] ]
V_37.mass = [ units[3] ]
V_37.temperature = [ units[4] ]
V_37.current = [ units[5] ]
V_37.light = [ units[6] ]

# 38
label = variables[38]["label"]
network = variables[38]["network"]
variable_type = variables[38]["type"]
label = variables[38]["label"]
doc = variables[38]["doc"]
onto_ID = "V_38"
V_38 = onto.ProMoVar( onto_ID )
V_38.label = label
V_38.network = network
V_38.variable_type = variable_type
V_38.comment = doc

units = variables[38]["units"].asList()
V_38.time = [ units[0] ]
V_38.length = [ units[1] ]
V_38.amount = [ units[2] ]
V_38.mass = [ units[3] ]
V_38.temperature = [ units[4] ]
V_38.current = [ units[5] ]
V_38.light = [ units[6] ]

# 40
label = variables[40]["label"]
network = variables[40]["network"]
variable_type = variables[40]["type"]
label = variables[40]["label"]
doc = variables[40]["doc"]
onto_ID = "V_40"
V_40 = onto.ProMoVar( onto_ID )
V_40.label = label
V_40.network = network
V_40.variable_type = variable_type
V_40.comment = doc

units = variables[40]["units"].asList()
V_40.time = [ units[0] ]
V_40.length = [ units[1] ]
V_40.amount = [ units[2] ]
V_40.mass = [ units[3] ]
V_40.temperature = [ units[4] ]
V_40.current = [ units[5] ]
V_40.light = [ units[6] ]

# 41
label = variables[41]["label"]
network = variables[41]["network"]
variable_type = variables[41]["type"]
label = variables[41]["label"]
doc = variables[41]["doc"]
onto_ID = "V_41"
V_41 = onto.ProMoVar( onto_ID )
V_41.label = label
V_41.network = network
V_41.variable_type = variable_type
V_41.comment = doc

units = variables[41]["units"].asList()
V_41.time = [ units[0] ]
V_41.length = [ units[1] ]
V_41.amount = [ units[2] ]
V_41.mass = [ units[3] ]
V_41.temperature = [ units[4] ]
V_41.current = [ units[5] ]
V_41.light = [ units[6] ]

# 42
label = variables[42]["label"]
network = variables[42]["network"]
variable_type = variables[42]["type"]
label = variables[42]["label"]
doc = variables[42]["doc"]
onto_ID = "V_42"
V_42 = onto.ProMoVar( onto_ID )
V_42.label = label
V_42.network = network
V_42.variable_type = variable_type
V_42.comment = doc

units = variables[42]["units"].asList()
V_42.time = [ units[0] ]
V_42.length = [ units[1] ]
V_42.amount = [ units[2] ]
V_42.mass = [ units[3] ]
V_42.temperature = [ units[4] ]
V_42.current = [ units[5] ]
V_42.light = [ units[6] ]

# 43
label = variables[43]["label"]
network = variables[43]["network"]
variable_type = variables[43]["type"]
label = variables[43]["label"]
doc = variables[43]["doc"]
onto_ID = "V_43"
V_43 = onto.ProMoVar( onto_ID )
V_43.label = label
V_43.network = network
V_43.variable_type = variable_type
V_43.comment = doc

units = variables[43]["units"].asList()
V_43.time = [ units[0] ]
V_43.length = [ units[1] ]
V_43.amount = [ units[2] ]
V_43.mass = [ units[3] ]
V_43.temperature = [ units[4] ]
V_43.current = [ units[5] ]
V_43.light = [ units[6] ]

# 44
label = variables[44]["label"]
network = variables[44]["network"]
variable_type = variables[44]["type"]
label = variables[44]["label"]
doc = variables[44]["doc"]
onto_ID = "V_44"
V_44 = onto.ProMoVar( onto_ID )
V_44.label = label
V_44.network = network
V_44.variable_type = variable_type
V_44.comment = doc

units = variables[44]["units"].asList()
V_44.time = [ units[0] ]
V_44.length = [ units[1] ]
V_44.amount = [ units[2] ]
V_44.mass = [ units[3] ]
V_44.temperature = [ units[4] ]
V_44.current = [ units[5] ]
V_44.light = [ units[6] ]

# 45
label = variables[45]["label"]
network = variables[45]["network"]
variable_type = variables[45]["type"]
label = variables[45]["label"]
doc = variables[45]["doc"]
onto_ID = "V_45"
V_45 = onto.ProMoVar( onto_ID )
V_45.label = label
V_45.network = network
V_45.variable_type = variable_type
V_45.comment = doc

units = variables[45]["units"].asList()
V_45.time = [ units[0] ]
V_45.length = [ units[1] ]
V_45.amount = [ units[2] ]
V_45.mass = [ units[3] ]
V_45.temperature = [ units[4] ]
V_45.current = [ units[5] ]
V_45.light = [ units[6] ]

# 46
label = variables[46]["label"]
network = variables[46]["network"]
variable_type = variables[46]["type"]
label = variables[46]["label"]
doc = variables[46]["doc"]
onto_ID = "V_46"
V_46 = onto.ProMoVar( onto_ID )
V_46.label = label
V_46.network = network
V_46.variable_type = variable_type
V_46.comment = doc

units = variables[46]["units"].asList()
V_46.time = [ units[0] ]
V_46.length = [ units[1] ]
V_46.amount = [ units[2] ]
V_46.mass = [ units[3] ]
V_46.temperature = [ units[4] ]
V_46.current = [ units[5] ]
V_46.light = [ units[6] ]

# 47
label = variables[47]["label"]
network = variables[47]["network"]
variable_type = variables[47]["type"]
label = variables[47]["label"]
doc = variables[47]["doc"]
onto_ID = "V_47"
V_47 = onto.ProMoVar( onto_ID )
V_47.label = label
V_47.network = network
V_47.variable_type = variable_type
V_47.comment = doc

units = variables[47]["units"].asList()
V_47.time = [ units[0] ]
V_47.length = [ units[1] ]
V_47.amount = [ units[2] ]
V_47.mass = [ units[3] ]
V_47.temperature = [ units[4] ]
V_47.current = [ units[5] ]
V_47.light = [ units[6] ]

# 48
label = variables[48]["label"]
network = variables[48]["network"]
variable_type = variables[48]["type"]
label = variables[48]["label"]
doc = variables[48]["doc"]
onto_ID = "V_48"
V_48 = onto.ProMoVar( onto_ID )
V_48.label = label
V_48.network = network
V_48.variable_type = variable_type
V_48.comment = doc

units = variables[48]["units"].asList()
V_48.time = [ units[0] ]
V_48.length = [ units[1] ]
V_48.amount = [ units[2] ]
V_48.mass = [ units[3] ]
V_48.temperature = [ units[4] ]
V_48.current = [ units[5] ]
V_48.light = [ units[6] ]

# 49
label = variables[49]["label"]
network = variables[49]["network"]
variable_type = variables[49]["type"]
label = variables[49]["label"]
doc = variables[49]["doc"]
onto_ID = "V_49"
V_49 = onto.ProMoVar( onto_ID )
V_49.label = label
V_49.network = network
V_49.variable_type = variable_type
V_49.comment = doc

units = variables[49]["units"].asList()
V_49.time = [ units[0] ]
V_49.length = [ units[1] ]
V_49.amount = [ units[2] ]
V_49.mass = [ units[3] ]
V_49.temperature = [ units[4] ]
V_49.current = [ units[5] ]
V_49.light = [ units[6] ]

# 50
label = variables[50]["label"]
network = variables[50]["network"]
variable_type = variables[50]["type"]
label = variables[50]["label"]
doc = variables[50]["doc"]
onto_ID = "V_50"
V_50 = onto.ProMoVar( onto_ID )
V_50.label = label
V_50.network = network
V_50.variable_type = variable_type
V_50.comment = doc

units = variables[50]["units"].asList()
V_50.time = [ units[0] ]
V_50.length = [ units[1] ]
V_50.amount = [ units[2] ]
V_50.mass = [ units[3] ]
V_50.temperature = [ units[4] ]
V_50.current = [ units[5] ]
V_50.light = [ units[6] ]

# 51
label = variables[51]["label"]
network = variables[51]["network"]
variable_type = variables[51]["type"]
label = variables[51]["label"]
doc = variables[51]["doc"]
onto_ID = "V_51"
V_51 = onto.ProMoVar( onto_ID )
V_51.label = label
V_51.network = network
V_51.variable_type = variable_type
V_51.comment = doc

units = variables[51]["units"].asList()
V_51.time = [ units[0] ]
V_51.length = [ units[1] ]
V_51.amount = [ units[2] ]
V_51.mass = [ units[3] ]
V_51.temperature = [ units[4] ]
V_51.current = [ units[5] ]
V_51.light = [ units[6] ]

# 52
label = variables[52]["label"]
network = variables[52]["network"]
variable_type = variables[52]["type"]
label = variables[52]["label"]
doc = variables[52]["doc"]
onto_ID = "V_52"
V_52 = onto.ProMoVar( onto_ID )
V_52.label = label
V_52.network = network
V_52.variable_type = variable_type
V_52.comment = doc

units = variables[52]["units"].asList()
V_52.time = [ units[0] ]
V_52.length = [ units[1] ]
V_52.amount = [ units[2] ]
V_52.mass = [ units[3] ]
V_52.temperature = [ units[4] ]
V_52.current = [ units[5] ]
V_52.light = [ units[6] ]

# 53
label = variables[53]["label"]
network = variables[53]["network"]
variable_type = variables[53]["type"]
label = variables[53]["label"]
doc = variables[53]["doc"]
onto_ID = "V_53"
V_53 = onto.ProMoVar( onto_ID )
V_53.label = label
V_53.network = network
V_53.variable_type = variable_type
V_53.comment = doc

units = variables[53]["units"].asList()
V_53.time = [ units[0] ]
V_53.length = [ units[1] ]
V_53.amount = [ units[2] ]
V_53.mass = [ units[3] ]
V_53.temperature = [ units[4] ]
V_53.current = [ units[5] ]
V_53.light = [ units[6] ]

# 54
label = variables[54]["label"]
network = variables[54]["network"]
variable_type = variables[54]["type"]
label = variables[54]["label"]
doc = variables[54]["doc"]
onto_ID = "V_54"
V_54 = onto.ProMoVar( onto_ID )
V_54.label = label
V_54.network = network
V_54.variable_type = variable_type
V_54.comment = doc

units = variables[54]["units"].asList()
V_54.time = [ units[0] ]
V_54.length = [ units[1] ]
V_54.amount = [ units[2] ]
V_54.mass = [ units[3] ]
V_54.temperature = [ units[4] ]
V_54.current = [ units[5] ]
V_54.light = [ units[6] ]

# 55
label = variables[55]["label"]
network = variables[55]["network"]
variable_type = variables[55]["type"]
label = variables[55]["label"]
doc = variables[55]["doc"]
onto_ID = "V_55"
V_55 = onto.ProMoVar( onto_ID )
V_55.label = label
V_55.network = network
V_55.variable_type = variable_type
V_55.comment = doc

units = variables[55]["units"].asList()
V_55.time = [ units[0] ]
V_55.length = [ units[1] ]
V_55.amount = [ units[2] ]
V_55.mass = [ units[3] ]
V_55.temperature = [ units[4] ]
V_55.current = [ units[5] ]
V_55.light = [ units[6] ]

# 56
label = variables[56]["label"]
network = variables[56]["network"]
variable_type = variables[56]["type"]
label = variables[56]["label"]
doc = variables[56]["doc"]
onto_ID = "V_56"
V_56 = onto.ProMoVar( onto_ID )
V_56.label = label
V_56.network = network
V_56.variable_type = variable_type
V_56.comment = doc

units = variables[56]["units"].asList()
V_56.time = [ units[0] ]
V_56.length = [ units[1] ]
V_56.amount = [ units[2] ]
V_56.mass = [ units[3] ]
V_56.temperature = [ units[4] ]
V_56.current = [ units[5] ]
V_56.light = [ units[6] ]

# 57
label = variables[57]["label"]
network = variables[57]["network"]
variable_type = variables[57]["type"]
label = variables[57]["label"]
doc = variables[57]["doc"]
onto_ID = "V_57"
V_57 = onto.ProMoVar( onto_ID )
V_57.label = label
V_57.network = network
V_57.variable_type = variable_type
V_57.comment = doc

units = variables[57]["units"].asList()
V_57.time = [ units[0] ]
V_57.length = [ units[1] ]
V_57.amount = [ units[2] ]
V_57.mass = [ units[3] ]
V_57.temperature = [ units[4] ]
V_57.current = [ units[5] ]
V_57.light = [ units[6] ]

# 58
label = variables[58]["label"]
network = variables[58]["network"]
variable_type = variables[58]["type"]
label = variables[58]["label"]
doc = variables[58]["doc"]
onto_ID = "V_58"
V_58 = onto.ProMoVar( onto_ID )
V_58.label = label
V_58.network = network
V_58.variable_type = variable_type
V_58.comment = doc

units = variables[58]["units"].asList()
V_58.time = [ units[0] ]
V_58.length = [ units[1] ]
V_58.amount = [ units[2] ]
V_58.mass = [ units[3] ]
V_58.temperature = [ units[4] ]
V_58.current = [ units[5] ]
V_58.light = [ units[6] ]

# 59
label = variables[59]["label"]
network = variables[59]["network"]
variable_type = variables[59]["type"]
label = variables[59]["label"]
doc = variables[59]["doc"]
onto_ID = "V_59"
V_59 = onto.ProMoVar( onto_ID )
V_59.label = label
V_59.network = network
V_59.variable_type = variable_type
V_59.comment = doc

units = variables[59]["units"].asList()
V_59.time = [ units[0] ]
V_59.length = [ units[1] ]
V_59.amount = [ units[2] ]
V_59.mass = [ units[3] ]
V_59.temperature = [ units[4] ]
V_59.current = [ units[5] ]
V_59.light = [ units[6] ]

# 60
label = variables[60]["label"]
network = variables[60]["network"]
variable_type = variables[60]["type"]
label = variables[60]["label"]
doc = variables[60]["doc"]
onto_ID = "V_60"
V_60 = onto.ProMoVar( onto_ID )
V_60.label = label
V_60.network = network
V_60.variable_type = variable_type
V_60.comment = doc

units = variables[60]["units"].asList()
V_60.time = [ units[0] ]
V_60.length = [ units[1] ]
V_60.amount = [ units[2] ]
V_60.mass = [ units[3] ]
V_60.temperature = [ units[4] ]
V_60.current = [ units[5] ]
V_60.light = [ units[6] ]

# 62
label = variables[62]["label"]
network = variables[62]["network"]
variable_type = variables[62]["type"]
label = variables[62]["label"]
doc = variables[62]["doc"]
onto_ID = "V_62"
V_62 = onto.ProMoVar( onto_ID )
V_62.label = label
V_62.network = network
V_62.variable_type = variable_type
V_62.comment = doc

units = variables[62]["units"].asList()
V_62.time = [ units[0] ]
V_62.length = [ units[1] ]
V_62.amount = [ units[2] ]
V_62.mass = [ units[3] ]
V_62.temperature = [ units[4] ]
V_62.current = [ units[5] ]
V_62.light = [ units[6] ]

# 63
label = variables[63]["label"]
network = variables[63]["network"]
variable_type = variables[63]["type"]
label = variables[63]["label"]
doc = variables[63]["doc"]
onto_ID = "V_63"
V_63 = onto.ProMoVar( onto_ID )
V_63.label = label
V_63.network = network
V_63.variable_type = variable_type
V_63.comment = doc

units = variables[63]["units"].asList()
V_63.time = [ units[0] ]
V_63.length = [ units[1] ]
V_63.amount = [ units[2] ]
V_63.mass = [ units[3] ]
V_63.temperature = [ units[4] ]
V_63.current = [ units[5] ]
V_63.light = [ units[6] ]

# 65
label = variables[65]["label"]
network = variables[65]["network"]
variable_type = variables[65]["type"]
label = variables[65]["label"]
doc = variables[65]["doc"]
onto_ID = "V_65"
V_65 = onto.ProMoVar( onto_ID )
V_65.label = label
V_65.network = network
V_65.variable_type = variable_type
V_65.comment = doc

units = variables[65]["units"].asList()
V_65.time = [ units[0] ]
V_65.length = [ units[1] ]
V_65.amount = [ units[2] ]
V_65.mass = [ units[3] ]
V_65.temperature = [ units[4] ]
V_65.current = [ units[5] ]
V_65.light = [ units[6] ]

# 66
label = variables[66]["label"]
network = variables[66]["network"]
variable_type = variables[66]["type"]
label = variables[66]["label"]
doc = variables[66]["doc"]
onto_ID = "V_66"
V_66 = onto.ProMoVar( onto_ID )
V_66.label = label
V_66.network = network
V_66.variable_type = variable_type
V_66.comment = doc

units = variables[66]["units"].asList()
V_66.time = [ units[0] ]
V_66.length = [ units[1] ]
V_66.amount = [ units[2] ]
V_66.mass = [ units[3] ]
V_66.temperature = [ units[4] ]
V_66.current = [ units[5] ]
V_66.light = [ units[6] ]

# 67
label = variables[67]["label"]
network = variables[67]["network"]
variable_type = variables[67]["type"]
label = variables[67]["label"]
doc = variables[67]["doc"]
onto_ID = "V_67"
V_67 = onto.ProMoVar( onto_ID )
V_67.label = label
V_67.network = network
V_67.variable_type = variable_type
V_67.comment = doc

units = variables[67]["units"].asList()
V_67.time = [ units[0] ]
V_67.length = [ units[1] ]
V_67.amount = [ units[2] ]
V_67.mass = [ units[3] ]
V_67.temperature = [ units[4] ]
V_67.current = [ units[5] ]
V_67.light = [ units[6] ]

# 70
label = variables[70]["label"]
network = variables[70]["network"]
variable_type = variables[70]["type"]
label = variables[70]["label"]
doc = variables[70]["doc"]
onto_ID = "V_70"
V_70 = onto.ProMoVar( onto_ID )
V_70.label = label
V_70.network = network
V_70.variable_type = variable_type
V_70.comment = doc

units = variables[70]["units"].asList()
V_70.time = [ units[0] ]
V_70.length = [ units[1] ]
V_70.amount = [ units[2] ]
V_70.mass = [ units[3] ]
V_70.temperature = [ units[4] ]
V_70.current = [ units[5] ]
V_70.light = [ units[6] ]

# 71
label = variables[71]["label"]
network = variables[71]["network"]
variable_type = variables[71]["type"]
label = variables[71]["label"]
doc = variables[71]["doc"]
onto_ID = "V_71"
V_71 = onto.ProMoVar( onto_ID )
V_71.label = label
V_71.network = network
V_71.variable_type = variable_type
V_71.comment = doc

units = variables[71]["units"].asList()
V_71.time = [ units[0] ]
V_71.length = [ units[1] ]
V_71.amount = [ units[2] ]
V_71.mass = [ units[3] ]
V_71.temperature = [ units[4] ]
V_71.current = [ units[5] ]
V_71.light = [ units[6] ]

# 72
label = variables[72]["label"]
network = variables[72]["network"]
variable_type = variables[72]["type"]
label = variables[72]["label"]
doc = variables[72]["doc"]
onto_ID = "V_72"
V_72 = onto.ProMoVar( onto_ID )
V_72.label = label
V_72.network = network
V_72.variable_type = variable_type
V_72.comment = doc

units = variables[72]["units"].asList()
V_72.time = [ units[0] ]
V_72.length = [ units[1] ]
V_72.amount = [ units[2] ]
V_72.mass = [ units[3] ]
V_72.temperature = [ units[4] ]
V_72.current = [ units[5] ]
V_72.light = [ units[6] ]

# 73
label = variables[73]["label"]
network = variables[73]["network"]
variable_type = variables[73]["type"]
label = variables[73]["label"]
doc = variables[73]["doc"]
onto_ID = "V_73"
V_73 = onto.ProMoVar( onto_ID )
V_73.label = label
V_73.network = network
V_73.variable_type = variable_type
V_73.comment = doc

units = variables[73]["units"].asList()
V_73.time = [ units[0] ]
V_73.length = [ units[1] ]
V_73.amount = [ units[2] ]
V_73.mass = [ units[3] ]
V_73.temperature = [ units[4] ]
V_73.current = [ units[5] ]
V_73.light = [ units[6] ]

# 74
label = variables[74]["label"]
network = variables[74]["network"]
variable_type = variables[74]["type"]
label = variables[74]["label"]
doc = variables[74]["doc"]
onto_ID = "V_74"
V_74 = onto.ProMoVar( onto_ID )
V_74.label = label
V_74.network = network
V_74.variable_type = variable_type
V_74.comment = doc

units = variables[74]["units"].asList()
V_74.time = [ units[0] ]
V_74.length = [ units[1] ]
V_74.amount = [ units[2] ]
V_74.mass = [ units[3] ]
V_74.temperature = [ units[4] ]
V_74.current = [ units[5] ]
V_74.light = [ units[6] ]

# 75
label = variables[75]["label"]
network = variables[75]["network"]
variable_type = variables[75]["type"]
label = variables[75]["label"]
doc = variables[75]["doc"]
onto_ID = "V_75"
V_75 = onto.ProMoVar( onto_ID )
V_75.label = label
V_75.network = network
V_75.variable_type = variable_type
V_75.comment = doc

units = variables[75]["units"].asList()
V_75.time = [ units[0] ]
V_75.length = [ units[1] ]
V_75.amount = [ units[2] ]
V_75.mass = [ units[3] ]
V_75.temperature = [ units[4] ]
V_75.current = [ units[5] ]
V_75.light = [ units[6] ]

# 76
label = variables[76]["label"]
network = variables[76]["network"]
variable_type = variables[76]["type"]
label = variables[76]["label"]
doc = variables[76]["doc"]
onto_ID = "V_76"
V_76 = onto.ProMoVar( onto_ID )
V_76.label = label
V_76.network = network
V_76.variable_type = variable_type
V_76.comment = doc

units = variables[76]["units"].asList()
V_76.time = [ units[0] ]
V_76.length = [ units[1] ]
V_76.amount = [ units[2] ]
V_76.mass = [ units[3] ]
V_76.temperature = [ units[4] ]
V_76.current = [ units[5] ]
V_76.light = [ units[6] ]

# 77
label = variables[77]["label"]
network = variables[77]["network"]
variable_type = variables[77]["type"]
label = variables[77]["label"]
doc = variables[77]["doc"]
onto_ID = "V_77"
V_77 = onto.ProMoVar( onto_ID )
V_77.label = label
V_77.network = network
V_77.variable_type = variable_type
V_77.comment = doc

units = variables[77]["units"].asList()
V_77.time = [ units[0] ]
V_77.length = [ units[1] ]
V_77.amount = [ units[2] ]
V_77.mass = [ units[3] ]
V_77.temperature = [ units[4] ]
V_77.current = [ units[5] ]
V_77.light = [ units[6] ]

# 78
label = variables[78]["label"]
network = variables[78]["network"]
variable_type = variables[78]["type"]
label = variables[78]["label"]
doc = variables[78]["doc"]
onto_ID = "V_78"
V_78 = onto.ProMoVar( onto_ID )
V_78.label = label
V_78.network = network
V_78.variable_type = variable_type
V_78.comment = doc

units = variables[78]["units"].asList()
V_78.time = [ units[0] ]
V_78.length = [ units[1] ]
V_78.amount = [ units[2] ]
V_78.mass = [ units[3] ]
V_78.temperature = [ units[4] ]
V_78.current = [ units[5] ]
V_78.light = [ units[6] ]

# 79
label = variables[79]["label"]
network = variables[79]["network"]
variable_type = variables[79]["type"]
label = variables[79]["label"]
doc = variables[79]["doc"]
onto_ID = "V_79"
V_79 = onto.ProMoVar( onto_ID )
V_79.label = label
V_79.network = network
V_79.variable_type = variable_type
V_79.comment = doc

units = variables[79]["units"].asList()
V_79.time = [ units[0] ]
V_79.length = [ units[1] ]
V_79.amount = [ units[2] ]
V_79.mass = [ units[3] ]
V_79.temperature = [ units[4] ]
V_79.current = [ units[5] ]
V_79.light = [ units[6] ]

# 80
label = variables[80]["label"]
network = variables[80]["network"]
variable_type = variables[80]["type"]
label = variables[80]["label"]
doc = variables[80]["doc"]
onto_ID = "V_80"
V_80 = onto.ProMoVar( onto_ID )
V_80.label = label
V_80.network = network
V_80.variable_type = variable_type
V_80.comment = doc

units = variables[80]["units"].asList()
V_80.time = [ units[0] ]
V_80.length = [ units[1] ]
V_80.amount = [ units[2] ]
V_80.mass = [ units[3] ]
V_80.temperature = [ units[4] ]
V_80.current = [ units[5] ]
V_80.light = [ units[6] ]

# 81
label = variables[81]["label"]
network = variables[81]["network"]
variable_type = variables[81]["type"]
label = variables[81]["label"]
doc = variables[81]["doc"]
onto_ID = "V_81"
V_81 = onto.ProMoVar( onto_ID )
V_81.label = label
V_81.network = network
V_81.variable_type = variable_type
V_81.comment = doc

units = variables[81]["units"].asList()
V_81.time = [ units[0] ]
V_81.length = [ units[1] ]
V_81.amount = [ units[2] ]
V_81.mass = [ units[3] ]
V_81.temperature = [ units[4] ]
V_81.current = [ units[5] ]
V_81.light = [ units[6] ]

# 82
label = variables[82]["label"]
network = variables[82]["network"]
variable_type = variables[82]["type"]
label = variables[82]["label"]
doc = variables[82]["doc"]
onto_ID = "V_82"
V_82 = onto.ProMoVar( onto_ID )
V_82.label = label
V_82.network = network
V_82.variable_type = variable_type
V_82.comment = doc

units = variables[82]["units"].asList()
V_82.time = [ units[0] ]
V_82.length = [ units[1] ]
V_82.amount = [ units[2] ]
V_82.mass = [ units[3] ]
V_82.temperature = [ units[4] ]
V_82.current = [ units[5] ]
V_82.light = [ units[6] ]

# 83
label = variables[83]["label"]
network = variables[83]["network"]
variable_type = variables[83]["type"]
label = variables[83]["label"]
doc = variables[83]["doc"]
onto_ID = "V_83"
V_83 = onto.ProMoVar( onto_ID )
V_83.label = label
V_83.network = network
V_83.variable_type = variable_type
V_83.comment = doc

units = variables[83]["units"].asList()
V_83.time = [ units[0] ]
V_83.length = [ units[1] ]
V_83.amount = [ units[2] ]
V_83.mass = [ units[3] ]
V_83.temperature = [ units[4] ]
V_83.current = [ units[5] ]
V_83.light = [ units[6] ]

# 84
label = variables[84]["label"]
network = variables[84]["network"]
variable_type = variables[84]["type"]
label = variables[84]["label"]
doc = variables[84]["doc"]
onto_ID = "V_84"
V_84 = onto.ProMoVar( onto_ID )
V_84.label = label
V_84.network = network
V_84.variable_type = variable_type
V_84.comment = doc

units = variables[84]["units"].asList()
V_84.time = [ units[0] ]
V_84.length = [ units[1] ]
V_84.amount = [ units[2] ]
V_84.mass = [ units[3] ]
V_84.temperature = [ units[4] ]
V_84.current = [ units[5] ]
V_84.light = [ units[6] ]

# 85
label = variables[85]["label"]
network = variables[85]["network"]
variable_type = variables[85]["type"]
label = variables[85]["label"]
doc = variables[85]["doc"]
onto_ID = "V_85"
V_85 = onto.ProMoVar( onto_ID )
V_85.label = label
V_85.network = network
V_85.variable_type = variable_type
V_85.comment = doc

units = variables[85]["units"].asList()
V_85.time = [ units[0] ]
V_85.length = [ units[1] ]
V_85.amount = [ units[2] ]
V_85.mass = [ units[3] ]
V_85.temperature = [ units[4] ]
V_85.current = [ units[5] ]
V_85.light = [ units[6] ]

# 86
label = variables[86]["label"]
network = variables[86]["network"]
variable_type = variables[86]["type"]
label = variables[86]["label"]
doc = variables[86]["doc"]
onto_ID = "V_86"
V_86 = onto.ProMoVar( onto_ID )
V_86.label = label
V_86.network = network
V_86.variable_type = variable_type
V_86.comment = doc

units = variables[86]["units"].asList()
V_86.time = [ units[0] ]
V_86.length = [ units[1] ]
V_86.amount = [ units[2] ]
V_86.mass = [ units[3] ]
V_86.temperature = [ units[4] ]
V_86.current = [ units[5] ]
V_86.light = [ units[6] ]

# 87
label = variables[87]["label"]
network = variables[87]["network"]
variable_type = variables[87]["type"]
label = variables[87]["label"]
doc = variables[87]["doc"]
onto_ID = "V_87"
V_87 = onto.ProMoVar( onto_ID )
V_87.label = label
V_87.network = network
V_87.variable_type = variable_type
V_87.comment = doc

units = variables[87]["units"].asList()
V_87.time = [ units[0] ]
V_87.length = [ units[1] ]
V_87.amount = [ units[2] ]
V_87.mass = [ units[3] ]
V_87.temperature = [ units[4] ]
V_87.current = [ units[5] ]
V_87.light = [ units[6] ]

# 88
label = variables[88]["label"]
network = variables[88]["network"]
variable_type = variables[88]["type"]
label = variables[88]["label"]
doc = variables[88]["doc"]
onto_ID = "V_88"
V_88 = onto.ProMoVar( onto_ID )
V_88.label = label
V_88.network = network
V_88.variable_type = variable_type
V_88.comment = doc

units = variables[88]["units"].asList()
V_88.time = [ units[0] ]
V_88.length = [ units[1] ]
V_88.amount = [ units[2] ]
V_88.mass = [ units[3] ]
V_88.temperature = [ units[4] ]
V_88.current = [ units[5] ]
V_88.light = [ units[6] ]

# 89
label = variables[89]["label"]
network = variables[89]["network"]
variable_type = variables[89]["type"]
label = variables[89]["label"]
doc = variables[89]["doc"]
onto_ID = "V_89"
V_89 = onto.ProMoVar( onto_ID )
V_89.label = label
V_89.network = network
V_89.variable_type = variable_type
V_89.comment = doc

units = variables[89]["units"].asList()
V_89.time = [ units[0] ]
V_89.length = [ units[1] ]
V_89.amount = [ units[2] ]
V_89.mass = [ units[3] ]
V_89.temperature = [ units[4] ]
V_89.current = [ units[5] ]
V_89.light = [ units[6] ]

# 90
label = variables[90]["label"]
network = variables[90]["network"]
variable_type = variables[90]["type"]
label = variables[90]["label"]
doc = variables[90]["doc"]
onto_ID = "V_90"
V_90 = onto.ProMoVar( onto_ID )
V_90.label = label
V_90.network = network
V_90.variable_type = variable_type
V_90.comment = doc

units = variables[90]["units"].asList()
V_90.time = [ units[0] ]
V_90.length = [ units[1] ]
V_90.amount = [ units[2] ]
V_90.mass = [ units[3] ]
V_90.temperature = [ units[4] ]
V_90.current = [ units[5] ]
V_90.light = [ units[6] ]

# 91
label = variables[91]["label"]
network = variables[91]["network"]
variable_type = variables[91]["type"]
label = variables[91]["label"]
doc = variables[91]["doc"]
onto_ID = "V_91"
V_91 = onto.ProMoVar( onto_ID )
V_91.label = label
V_91.network = network
V_91.variable_type = variable_type
V_91.comment = doc

units = variables[91]["units"].asList()
V_91.time = [ units[0] ]
V_91.length = [ units[1] ]
V_91.amount = [ units[2] ]
V_91.mass = [ units[3] ]
V_91.temperature = [ units[4] ]
V_91.current = [ units[5] ]
V_91.light = [ units[6] ]

# 92
label = variables[92]["label"]
network = variables[92]["network"]
variable_type = variables[92]["type"]
label = variables[92]["label"]
doc = variables[92]["doc"]
onto_ID = "V_92"
V_92 = onto.ProMoVar( onto_ID )
V_92.label = label
V_92.network = network
V_92.variable_type = variable_type
V_92.comment = doc

units = variables[92]["units"].asList()
V_92.time = [ units[0] ]
V_92.length = [ units[1] ]
V_92.amount = [ units[2] ]
V_92.mass = [ units[3] ]
V_92.temperature = [ units[4] ]
V_92.current = [ units[5] ]
V_92.light = [ units[6] ]

# 93
label = variables[93]["label"]
network = variables[93]["network"]
variable_type = variables[93]["type"]
label = variables[93]["label"]
doc = variables[93]["doc"]
onto_ID = "V_93"
V_93 = onto.ProMoVar( onto_ID )
V_93.label = label
V_93.network = network
V_93.variable_type = variable_type
V_93.comment = doc

units = variables[93]["units"].asList()
V_93.time = [ units[0] ]
V_93.length = [ units[1] ]
V_93.amount = [ units[2] ]
V_93.mass = [ units[3] ]
V_93.temperature = [ units[4] ]
V_93.current = [ units[5] ]
V_93.light = [ units[6] ]

# 94
label = variables[94]["label"]
network = variables[94]["network"]
variable_type = variables[94]["type"]
label = variables[94]["label"]
doc = variables[94]["doc"]
onto_ID = "V_94"
V_94 = onto.ProMoVar( onto_ID )
V_94.label = label
V_94.network = network
V_94.variable_type = variable_type
V_94.comment = doc

units = variables[94]["units"].asList()
V_94.time = [ units[0] ]
V_94.length = [ units[1] ]
V_94.amount = [ units[2] ]
V_94.mass = [ units[3] ]
V_94.temperature = [ units[4] ]
V_94.current = [ units[5] ]
V_94.light = [ units[6] ]

# 95
label = variables[95]["label"]
network = variables[95]["network"]
variable_type = variables[95]["type"]
label = variables[95]["label"]
doc = variables[95]["doc"]
onto_ID = "V_95"
V_95 = onto.ProMoVar( onto_ID )
V_95.label = label
V_95.network = network
V_95.variable_type = variable_type
V_95.comment = doc

units = variables[95]["units"].asList()
V_95.time = [ units[0] ]
V_95.length = [ units[1] ]
V_95.amount = [ units[2] ]
V_95.mass = [ units[3] ]
V_95.temperature = [ units[4] ]
V_95.current = [ units[5] ]
V_95.light = [ units[6] ]

# 96
label = variables[96]["label"]
network = variables[96]["network"]
variable_type = variables[96]["type"]
label = variables[96]["label"]
doc = variables[96]["doc"]
onto_ID = "V_96"
V_96 = onto.ProMoVar( onto_ID )
V_96.label = label
V_96.network = network
V_96.variable_type = variable_type
V_96.comment = doc

units = variables[96]["units"].asList()
V_96.time = [ units[0] ]
V_96.length = [ units[1] ]
V_96.amount = [ units[2] ]
V_96.mass = [ units[3] ]
V_96.temperature = [ units[4] ]
V_96.current = [ units[5] ]
V_96.light = [ units[6] ]

# 97
label = variables[97]["label"]
network = variables[97]["network"]
variable_type = variables[97]["type"]
label = variables[97]["label"]
doc = variables[97]["doc"]
onto_ID = "V_97"
V_97 = onto.ProMoVar( onto_ID )
V_97.label = label
V_97.network = network
V_97.variable_type = variable_type
V_97.comment = doc

units = variables[97]["units"].asList()
V_97.time = [ units[0] ]
V_97.length = [ units[1] ]
V_97.amount = [ units[2] ]
V_97.mass = [ units[3] ]
V_97.temperature = [ units[4] ]
V_97.current = [ units[5] ]
V_97.light = [ units[6] ]

# 98
label = variables[98]["label"]
network = variables[98]["network"]
variable_type = variables[98]["type"]
label = variables[98]["label"]
doc = variables[98]["doc"]
onto_ID = "V_98"
V_98 = onto.ProMoVar( onto_ID )
V_98.label = label
V_98.network = network
V_98.variable_type = variable_type
V_98.comment = doc

units = variables[98]["units"].asList()
V_98.time = [ units[0] ]
V_98.length = [ units[1] ]
V_98.amount = [ units[2] ]
V_98.mass = [ units[3] ]
V_98.temperature = [ units[4] ]
V_98.current = [ units[5] ]
V_98.light = [ units[6] ]

# 99
label = variables[99]["label"]
network = variables[99]["network"]
variable_type = variables[99]["type"]
label = variables[99]["label"]
doc = variables[99]["doc"]
onto_ID = "V_99"
V_99 = onto.ProMoVar( onto_ID )
V_99.label = label
V_99.network = network
V_99.variable_type = variable_type
V_99.comment = doc

units = variables[99]["units"].asList()
V_99.time = [ units[0] ]
V_99.length = [ units[1] ]
V_99.amount = [ units[2] ]
V_99.mass = [ units[3] ]
V_99.temperature = [ units[4] ]
V_99.current = [ units[5] ]
V_99.light = [ units[6] ]

# 100
label = variables[100]["label"]
network = variables[100]["network"]
variable_type = variables[100]["type"]
label = variables[100]["label"]
doc = variables[100]["doc"]
onto_ID = "V_100"
V_100 = onto.ProMoVar( onto_ID )
V_100.label = label
V_100.network = network
V_100.variable_type = variable_type
V_100.comment = doc

units = variables[100]["units"].asList()
V_100.time = [ units[0] ]
V_100.length = [ units[1] ]
V_100.amount = [ units[2] ]
V_100.mass = [ units[3] ]
V_100.temperature = [ units[4] ]
V_100.current = [ units[5] ]
V_100.light = [ units[6] ]

# 101
label = variables[101]["label"]
network = variables[101]["network"]
variable_type = variables[101]["type"]
label = variables[101]["label"]
doc = variables[101]["doc"]
onto_ID = "V_101"
V_101 = onto.ProMoVar( onto_ID )
V_101.label = label
V_101.network = network
V_101.variable_type = variable_type
V_101.comment = doc

units = variables[101]["units"].asList()
V_101.time = [ units[0] ]
V_101.length = [ units[1] ]
V_101.amount = [ units[2] ]
V_101.mass = [ units[3] ]
V_101.temperature = [ units[4] ]
V_101.current = [ units[5] ]
V_101.light = [ units[6] ]

# 102
label = variables[102]["label"]
network = variables[102]["network"]
variable_type = variables[102]["type"]
label = variables[102]["label"]
doc = variables[102]["doc"]
onto_ID = "V_102"
V_102 = onto.ProMoVar( onto_ID )
V_102.label = label
V_102.network = network
V_102.variable_type = variable_type
V_102.comment = doc

units = variables[102]["units"].asList()
V_102.time = [ units[0] ]
V_102.length = [ units[1] ]
V_102.amount = [ units[2] ]
V_102.mass = [ units[3] ]
V_102.temperature = [ units[4] ]
V_102.current = [ units[5] ]
V_102.light = [ units[6] ]

# 103
label = variables[103]["label"]
network = variables[103]["network"]
variable_type = variables[103]["type"]
label = variables[103]["label"]
doc = variables[103]["doc"]
onto_ID = "V_103"
V_103 = onto.ProMoVar( onto_ID )
V_103.label = label
V_103.network = network
V_103.variable_type = variable_type
V_103.comment = doc

units = variables[103]["units"].asList()
V_103.time = [ units[0] ]
V_103.length = [ units[1] ]
V_103.amount = [ units[2] ]
V_103.mass = [ units[3] ]
V_103.temperature = [ units[4] ]
V_103.current = [ units[5] ]
V_103.light = [ units[6] ]

# 104
label = variables[104]["label"]
network = variables[104]["network"]
variable_type = variables[104]["type"]
label = variables[104]["label"]
doc = variables[104]["doc"]
onto_ID = "V_104"
V_104 = onto.ProMoVar( onto_ID )
V_104.label = label
V_104.network = network
V_104.variable_type = variable_type
V_104.comment = doc

units = variables[104]["units"].asList()
V_104.time = [ units[0] ]
V_104.length = [ units[1] ]
V_104.amount = [ units[2] ]
V_104.mass = [ units[3] ]
V_104.temperature = [ units[4] ]
V_104.current = [ units[5] ]
V_104.light = [ units[6] ]

# 105
label = variables[105]["label"]
network = variables[105]["network"]
variable_type = variables[105]["type"]
label = variables[105]["label"]
doc = variables[105]["doc"]
onto_ID = "V_105"
V_105 = onto.ProMoVar( onto_ID )
V_105.label = label
V_105.network = network
V_105.variable_type = variable_type
V_105.comment = doc

units = variables[105]["units"].asList()
V_105.time = [ units[0] ]
V_105.length = [ units[1] ]
V_105.amount = [ units[2] ]
V_105.mass = [ units[3] ]
V_105.temperature = [ units[4] ]
V_105.current = [ units[5] ]
V_105.light = [ units[6] ]

# 106
label = variables[106]["label"]
network = variables[106]["network"]
variable_type = variables[106]["type"]
label = variables[106]["label"]
doc = variables[106]["doc"]
onto_ID = "V_106"
V_106 = onto.ProMoVar( onto_ID )
V_106.label = label
V_106.network = network
V_106.variable_type = variable_type
V_106.comment = doc

units = variables[106]["units"].asList()
V_106.time = [ units[0] ]
V_106.length = [ units[1] ]
V_106.amount = [ units[2] ]
V_106.mass = [ units[3] ]
V_106.temperature = [ units[4] ]
V_106.current = [ units[5] ]
V_106.light = [ units[6] ]

# 107
label = variables[107]["label"]
network = variables[107]["network"]
variable_type = variables[107]["type"]
label = variables[107]["label"]
doc = variables[107]["doc"]
onto_ID = "V_107"
V_107 = onto.ProMoVar( onto_ID )
V_107.label = label
V_107.network = network
V_107.variable_type = variable_type
V_107.comment = doc

units = variables[107]["units"].asList()
V_107.time = [ units[0] ]
V_107.length = [ units[1] ]
V_107.amount = [ units[2] ]
V_107.mass = [ units[3] ]
V_107.temperature = [ units[4] ]
V_107.current = [ units[5] ]
V_107.light = [ units[6] ]

# 108
label = variables[108]["label"]
network = variables[108]["network"]
variable_type = variables[108]["type"]
label = variables[108]["label"]
doc = variables[108]["doc"]
onto_ID = "V_108"
V_108 = onto.ProMoVar( onto_ID )
V_108.label = label
V_108.network = network
V_108.variable_type = variable_type
V_108.comment = doc

units = variables[108]["units"].asList()
V_108.time = [ units[0] ]
V_108.length = [ units[1] ]
V_108.amount = [ units[2] ]
V_108.mass = [ units[3] ]
V_108.temperature = [ units[4] ]
V_108.current = [ units[5] ]
V_108.light = [ units[6] ]

# 109
label = variables[109]["label"]
network = variables[109]["network"]
variable_type = variables[109]["type"]
label = variables[109]["label"]
doc = variables[109]["doc"]
onto_ID = "V_109"
V_109 = onto.ProMoVar( onto_ID )
V_109.label = label
V_109.network = network
V_109.variable_type = variable_type
V_109.comment = doc

units = variables[109]["units"].asList()
V_109.time = [ units[0] ]
V_109.length = [ units[1] ]
V_109.amount = [ units[2] ]
V_109.mass = [ units[3] ]
V_109.temperature = [ units[4] ]
V_109.current = [ units[5] ]
V_109.light = [ units[6] ]

# 110
label = variables[110]["label"]
network = variables[110]["network"]
variable_type = variables[110]["type"]
label = variables[110]["label"]
doc = variables[110]["doc"]
onto_ID = "V_110"
V_110 = onto.ProMoVar( onto_ID )
V_110.label = label
V_110.network = network
V_110.variable_type = variable_type
V_110.comment = doc

units = variables[110]["units"].asList()
V_110.time = [ units[0] ]
V_110.length = [ units[1] ]
V_110.amount = [ units[2] ]
V_110.mass = [ units[3] ]
V_110.temperature = [ units[4] ]
V_110.current = [ units[5] ]
V_110.light = [ units[6] ]

# 112
label = variables[112]["label"]
network = variables[112]["network"]
variable_type = variables[112]["type"]
label = variables[112]["label"]
doc = variables[112]["doc"]
onto_ID = "V_112"
V_112 = onto.ProMoVar( onto_ID )
V_112.label = label
V_112.network = network
V_112.variable_type = variable_type
V_112.comment = doc

units = variables[112]["units"].asList()
V_112.time = [ units[0] ]
V_112.length = [ units[1] ]
V_112.amount = [ units[2] ]
V_112.mass = [ units[3] ]
V_112.temperature = [ units[4] ]
V_112.current = [ units[5] ]
V_112.light = [ units[6] ]

# 113
label = variables[113]["label"]
network = variables[113]["network"]
variable_type = variables[113]["type"]
label = variables[113]["label"]
doc = variables[113]["doc"]
onto_ID = "V_113"
V_113 = onto.ProMoVar( onto_ID )
V_113.label = label
V_113.network = network
V_113.variable_type = variable_type
V_113.comment = doc

units = variables[113]["units"].asList()
V_113.time = [ units[0] ]
V_113.length = [ units[1] ]
V_113.amount = [ units[2] ]
V_113.mass = [ units[3] ]
V_113.temperature = [ units[4] ]
V_113.current = [ units[5] ]
V_113.light = [ units[6] ]

# 114
label = variables[114]["label"]
network = variables[114]["network"]
variable_type = variables[114]["type"]
label = variables[114]["label"]
doc = variables[114]["doc"]
onto_ID = "V_114"
V_114 = onto.ProMoVar( onto_ID )
V_114.label = label
V_114.network = network
V_114.variable_type = variable_type
V_114.comment = doc

units = variables[114]["units"].asList()
V_114.time = [ units[0] ]
V_114.length = [ units[1] ]
V_114.amount = [ units[2] ]
V_114.mass = [ units[3] ]
V_114.temperature = [ units[4] ]
V_114.current = [ units[5] ]
V_114.light = [ units[6] ]

# 115
label = variables[115]["label"]
network = variables[115]["network"]
variable_type = variables[115]["type"]
label = variables[115]["label"]
doc = variables[115]["doc"]
onto_ID = "V_115"
V_115 = onto.ProMoVar( onto_ID )
V_115.label = label
V_115.network = network
V_115.variable_type = variable_type
V_115.comment = doc

units = variables[115]["units"].asList()
V_115.time = [ units[0] ]
V_115.length = [ units[1] ]
V_115.amount = [ units[2] ]
V_115.mass = [ units[3] ]
V_115.temperature = [ units[4] ]
V_115.current = [ units[5] ]
V_115.light = [ units[6] ]

# 116
label = variables[116]["label"]
network = variables[116]["network"]
variable_type = variables[116]["type"]
label = variables[116]["label"]
doc = variables[116]["doc"]
onto_ID = "V_116"
V_116 = onto.ProMoVar( onto_ID )
V_116.label = label
V_116.network = network
V_116.variable_type = variable_type
V_116.comment = doc

units = variables[116]["units"].asList()
V_116.time = [ units[0] ]
V_116.length = [ units[1] ]
V_116.amount = [ units[2] ]
V_116.mass = [ units[3] ]
V_116.temperature = [ units[4] ]
V_116.current = [ units[5] ]
V_116.light = [ units[6] ]

# 117
label = variables[117]["label"]
network = variables[117]["network"]
variable_type = variables[117]["type"]
label = variables[117]["label"]
doc = variables[117]["doc"]
onto_ID = "V_117"
V_117 = onto.ProMoVar( onto_ID )
V_117.label = label
V_117.network = network
V_117.variable_type = variable_type
V_117.comment = doc

units = variables[117]["units"].asList()
V_117.time = [ units[0] ]
V_117.length = [ units[1] ]
V_117.amount = [ units[2] ]
V_117.mass = [ units[3] ]
V_117.temperature = [ units[4] ]
V_117.current = [ units[5] ]
V_117.light = [ units[6] ]

# 118
label = variables[118]["label"]
network = variables[118]["network"]
variable_type = variables[118]["type"]
label = variables[118]["label"]
doc = variables[118]["doc"]
onto_ID = "V_118"
V_118 = onto.ProMoVar( onto_ID )
V_118.label = label
V_118.network = network
V_118.variable_type = variable_type
V_118.comment = doc

units = variables[118]["units"].asList()
V_118.time = [ units[0] ]
V_118.length = [ units[1] ]
V_118.amount = [ units[2] ]
V_118.mass = [ units[3] ]
V_118.temperature = [ units[4] ]
V_118.current = [ units[5] ]
V_118.light = [ units[6] ]

# 119
label = variables[119]["label"]
network = variables[119]["network"]
variable_type = variables[119]["type"]
label = variables[119]["label"]
doc = variables[119]["doc"]
onto_ID = "V_119"
V_119 = onto.ProMoVar( onto_ID )
V_119.label = label
V_119.network = network
V_119.variable_type = variable_type
V_119.comment = doc

units = variables[119]["units"].asList()
V_119.time = [ units[0] ]
V_119.length = [ units[1] ]
V_119.amount = [ units[2] ]
V_119.mass = [ units[3] ]
V_119.temperature = [ units[4] ]
V_119.current = [ units[5] ]
V_119.light = [ units[6] ]

# 124
label = variables[124]["label"]
network = variables[124]["network"]
variable_type = variables[124]["type"]
label = variables[124]["label"]
doc = variables[124]["doc"]
onto_ID = "V_124"
V_124 = onto.ProMoVar( onto_ID )
V_124.label = label
V_124.network = network
V_124.variable_type = variable_type
V_124.comment = doc

units = variables[124]["units"].asList()
V_124.time = [ units[0] ]
V_124.length = [ units[1] ]
V_124.amount = [ units[2] ]
V_124.mass = [ units[3] ]
V_124.temperature = [ units[4] ]
V_124.current = [ units[5] ]
V_124.light = [ units[6] ]

# 125
label = variables[125]["label"]
network = variables[125]["network"]
variable_type = variables[125]["type"]
label = variables[125]["label"]
doc = variables[125]["doc"]
onto_ID = "V_125"
V_125 = onto.ProMoVar( onto_ID )
V_125.label = label
V_125.network = network
V_125.variable_type = variable_type
V_125.comment = doc

units = variables[125]["units"].asList()
V_125.time = [ units[0] ]
V_125.length = [ units[1] ]
V_125.amount = [ units[2] ]
V_125.mass = [ units[3] ]
V_125.temperature = [ units[4] ]
V_125.current = [ units[5] ]
V_125.light = [ units[6] ]

# 126
label = variables[126]["label"]
network = variables[126]["network"]
variable_type = variables[126]["type"]
label = variables[126]["label"]
doc = variables[126]["doc"]
onto_ID = "V_126"
V_126 = onto.ProMoVar( onto_ID )
V_126.label = label
V_126.network = network
V_126.variable_type = variable_type
V_126.comment = doc

units = variables[126]["units"].asList()
V_126.time = [ units[0] ]
V_126.length = [ units[1] ]
V_126.amount = [ units[2] ]
V_126.mass = [ units[3] ]
V_126.temperature = [ units[4] ]
V_126.current = [ units[5] ]
V_126.light = [ units[6] ]

# 127
label = variables[127]["label"]
network = variables[127]["network"]
variable_type = variables[127]["type"]
label = variables[127]["label"]
doc = variables[127]["doc"]
onto_ID = "V_127"
V_127 = onto.ProMoVar( onto_ID )
V_127.label = label
V_127.network = network
V_127.variable_type = variable_type
V_127.comment = doc

units = variables[127]["units"].asList()
V_127.time = [ units[0] ]
V_127.length = [ units[1] ]
V_127.amount = [ units[2] ]
V_127.mass = [ units[3] ]
V_127.temperature = [ units[4] ]
V_127.current = [ units[5] ]
V_127.light = [ units[6] ]

# 128
label = variables[128]["label"]
network = variables[128]["network"]
variable_type = variables[128]["type"]
label = variables[128]["label"]
doc = variables[128]["doc"]
onto_ID = "V_128"
V_128 = onto.ProMoVar( onto_ID )
V_128.label = label
V_128.network = network
V_128.variable_type = variable_type
V_128.comment = doc

units = variables[128]["units"].asList()
V_128.time = [ units[0] ]
V_128.length = [ units[1] ]
V_128.amount = [ units[2] ]
V_128.mass = [ units[3] ]
V_128.temperature = [ units[4] ]
V_128.current = [ units[5] ]
V_128.light = [ units[6] ]

# 129
label = variables[129]["label"]
network = variables[129]["network"]
variable_type = variables[129]["type"]
label = variables[129]["label"]
doc = variables[129]["doc"]
onto_ID = "V_129"
V_129 = onto.ProMoVar( onto_ID )
V_129.label = label
V_129.network = network
V_129.variable_type = variable_type
V_129.comment = doc

units = variables[129]["units"].asList()
V_129.time = [ units[0] ]
V_129.length = [ units[1] ]
V_129.amount = [ units[2] ]
V_129.mass = [ units[3] ]
V_129.temperature = [ units[4] ]
V_129.current = [ units[5] ]
V_129.light = [ units[6] ]

# 130
label = variables[130]["label"]
network = variables[130]["network"]
variable_type = variables[130]["type"]
label = variables[130]["label"]
doc = variables[130]["doc"]
onto_ID = "V_130"
V_130 = onto.ProMoVar( onto_ID )
V_130.label = label
V_130.network = network
V_130.variable_type = variable_type
V_130.comment = doc

units = variables[130]["units"].asList()
V_130.time = [ units[0] ]
V_130.length = [ units[1] ]
V_130.amount = [ units[2] ]
V_130.mass = [ units[3] ]
V_130.temperature = [ units[4] ]
V_130.current = [ units[5] ]
V_130.light = [ units[6] ]

# 131
label = variables[131]["label"]
network = variables[131]["network"]
variable_type = variables[131]["type"]
label = variables[131]["label"]
doc = variables[131]["doc"]
onto_ID = "V_131"
V_131 = onto.ProMoVar( onto_ID )
V_131.label = label
V_131.network = network
V_131.variable_type = variable_type
V_131.comment = doc

units = variables[131]["units"].asList()
V_131.time = [ units[0] ]
V_131.length = [ units[1] ]
V_131.amount = [ units[2] ]
V_131.mass = [ units[3] ]
V_131.temperature = [ units[4] ]
V_131.current = [ units[5] ]
V_131.light = [ units[6] ]

# 132
label = variables[132]["label"]
network = variables[132]["network"]
variable_type = variables[132]["type"]
label = variables[132]["label"]
doc = variables[132]["doc"]
onto_ID = "V_132"
V_132 = onto.ProMoVar( onto_ID )
V_132.label = label
V_132.network = network
V_132.variable_type = variable_type
V_132.comment = doc

units = variables[132]["units"].asList()
V_132.time = [ units[0] ]
V_132.length = [ units[1] ]
V_132.amount = [ units[2] ]
V_132.mass = [ units[3] ]
V_132.temperature = [ units[4] ]
V_132.current = [ units[5] ]
V_132.light = [ units[6] ]

# 133
label = variables[133]["label"]
network = variables[133]["network"]
variable_type = variables[133]["type"]
label = variables[133]["label"]
doc = variables[133]["doc"]
onto_ID = "V_133"
V_133 = onto.ProMoVar( onto_ID )
V_133.label = label
V_133.network = network
V_133.variable_type = variable_type
V_133.comment = doc

units = variables[133]["units"].asList()
V_133.time = [ units[0] ]
V_133.length = [ units[1] ]
V_133.amount = [ units[2] ]
V_133.mass = [ units[3] ]
V_133.temperature = [ units[4] ]
V_133.current = [ units[5] ]
V_133.light = [ units[6] ]

# 134
label = variables[134]["label"]
network = variables[134]["network"]
variable_type = variables[134]["type"]
label = variables[134]["label"]
doc = variables[134]["doc"]
onto_ID = "V_134"
V_134 = onto.ProMoVar( onto_ID )
V_134.label = label
V_134.network = network
V_134.variable_type = variable_type
V_134.comment = doc

units = variables[134]["units"].asList()
V_134.time = [ units[0] ]
V_134.length = [ units[1] ]
V_134.amount = [ units[2] ]
V_134.mass = [ units[3] ]
V_134.temperature = [ units[4] ]
V_134.current = [ units[5] ]
V_134.light = [ units[6] ]

# 135
label = variables[135]["label"]
network = variables[135]["network"]
variable_type = variables[135]["type"]
label = variables[135]["label"]
doc = variables[135]["doc"]
onto_ID = "V_135"
V_135 = onto.ProMoVar( onto_ID )
V_135.label = label
V_135.network = network
V_135.variable_type = variable_type
V_135.comment = doc

units = variables[135]["units"].asList()
V_135.time = [ units[0] ]
V_135.length = [ units[1] ]
V_135.amount = [ units[2] ]
V_135.mass = [ units[3] ]
V_135.temperature = [ units[4] ]
V_135.current = [ units[5] ]
V_135.light = [ units[6] ]

# 136
label = variables[136]["label"]
network = variables[136]["network"]
variable_type = variables[136]["type"]
label = variables[136]["label"]
doc = variables[136]["doc"]
onto_ID = "V_136"
V_136 = onto.ProMoVar( onto_ID )
V_136.label = label
V_136.network = network
V_136.variable_type = variable_type
V_136.comment = doc

units = variables[136]["units"].asList()
V_136.time = [ units[0] ]
V_136.length = [ units[1] ]
V_136.amount = [ units[2] ]
V_136.mass = [ units[3] ]
V_136.temperature = [ units[4] ]
V_136.current = [ units[5] ]
V_136.light = [ units[6] ]

# 137
label = variables[137]["label"]
network = variables[137]["network"]
variable_type = variables[137]["type"]
label = variables[137]["label"]
doc = variables[137]["doc"]
onto_ID = "V_137"
V_137 = onto.ProMoVar( onto_ID )
V_137.label = label
V_137.network = network
V_137.variable_type = variable_type
V_137.comment = doc

units = variables[137]["units"].asList()
V_137.time = [ units[0] ]
V_137.length = [ units[1] ]
V_137.amount = [ units[2] ]
V_137.mass = [ units[3] ]
V_137.temperature = [ units[4] ]
V_137.current = [ units[5] ]
V_137.light = [ units[6] ]

# 138
label = variables[138]["label"]
network = variables[138]["network"]
variable_type = variables[138]["type"]
label = variables[138]["label"]
doc = variables[138]["doc"]
onto_ID = "V_138"
V_138 = onto.ProMoVar( onto_ID )
V_138.label = label
V_138.network = network
V_138.variable_type = variable_type
V_138.comment = doc

units = variables[138]["units"].asList()
V_138.time = [ units[0] ]
V_138.length = [ units[1] ]
V_138.amount = [ units[2] ]
V_138.mass = [ units[3] ]
V_138.temperature = [ units[4] ]
V_138.current = [ units[5] ]
V_138.light = [ units[6] ]

# 139
label = variables[139]["label"]
network = variables[139]["network"]
variable_type = variables[139]["type"]
label = variables[139]["label"]
doc = variables[139]["doc"]
onto_ID = "V_139"
V_139 = onto.ProMoVar( onto_ID )
V_139.label = label
V_139.network = network
V_139.variable_type = variable_type
V_139.comment = doc

units = variables[139]["units"].asList()
V_139.time = [ units[0] ]
V_139.length = [ units[1] ]
V_139.amount = [ units[2] ]
V_139.mass = [ units[3] ]
V_139.temperature = [ units[4] ]
V_139.current = [ units[5] ]
V_139.light = [ units[6] ]

# 140
label = variables[140]["label"]
network = variables[140]["network"]
variable_type = variables[140]["type"]
label = variables[140]["label"]
doc = variables[140]["doc"]
onto_ID = "V_140"
V_140 = onto.ProMoVar( onto_ID )
V_140.label = label
V_140.network = network
V_140.variable_type = variable_type
V_140.comment = doc

units = variables[140]["units"].asList()
V_140.time = [ units[0] ]
V_140.length = [ units[1] ]
V_140.amount = [ units[2] ]
V_140.mass = [ units[3] ]
V_140.temperature = [ units[4] ]
V_140.current = [ units[5] ]
V_140.light = [ units[6] ]

# 141
label = variables[141]["label"]
network = variables[141]["network"]
variable_type = variables[141]["type"]
label = variables[141]["label"]
doc = variables[141]["doc"]
onto_ID = "V_141"
V_141 = onto.ProMoVar( onto_ID )
V_141.label = label
V_141.network = network
V_141.variable_type = variable_type
V_141.comment = doc

units = variables[141]["units"].asList()
V_141.time = [ units[0] ]
V_141.length = [ units[1] ]
V_141.amount = [ units[2] ]
V_141.mass = [ units[3] ]
V_141.temperature = [ units[4] ]
V_141.current = [ units[5] ]
V_141.light = [ units[6] ]

# 142
label = variables[142]["label"]
network = variables[142]["network"]
variable_type = variables[142]["type"]
label = variables[142]["label"]
doc = variables[142]["doc"]
onto_ID = "V_142"
V_142 = onto.ProMoVar( onto_ID )
V_142.label = label
V_142.network = network
V_142.variable_type = variable_type
V_142.comment = doc

units = variables[142]["units"].asList()
V_142.time = [ units[0] ]
V_142.length = [ units[1] ]
V_142.amount = [ units[2] ]
V_142.mass = [ units[3] ]
V_142.temperature = [ units[4] ]
V_142.current = [ units[5] ]
V_142.light = [ units[6] ]

# 143
label = variables[143]["label"]
network = variables[143]["network"]
variable_type = variables[143]["type"]
label = variables[143]["label"]
doc = variables[143]["doc"]
onto_ID = "V_143"
V_143 = onto.ProMoVar( onto_ID )
V_143.label = label
V_143.network = network
V_143.variable_type = variable_type
V_143.comment = doc

units = variables[143]["units"].asList()
V_143.time = [ units[0] ]
V_143.length = [ units[1] ]
V_143.amount = [ units[2] ]
V_143.mass = [ units[3] ]
V_143.temperature = [ units[4] ]
V_143.current = [ units[5] ]
V_143.light = [ units[6] ]

# 144
label = variables[144]["label"]
network = variables[144]["network"]
variable_type = variables[144]["type"]
label = variables[144]["label"]
doc = variables[144]["doc"]
onto_ID = "V_144"
V_144 = onto.ProMoVar( onto_ID )
V_144.label = label
V_144.network = network
V_144.variable_type = variable_type
V_144.comment = doc

units = variables[144]["units"].asList()
V_144.time = [ units[0] ]
V_144.length = [ units[1] ]
V_144.amount = [ units[2] ]
V_144.mass = [ units[3] ]
V_144.temperature = [ units[4] ]
V_144.current = [ units[5] ]
V_144.light = [ units[6] ]

# 145
label = variables[145]["label"]
network = variables[145]["network"]
variable_type = variables[145]["type"]
label = variables[145]["label"]
doc = variables[145]["doc"]
onto_ID = "V_145"
V_145 = onto.ProMoVar( onto_ID )
V_145.label = label
V_145.network = network
V_145.variable_type = variable_type
V_145.comment = doc

units = variables[145]["units"].asList()
V_145.time = [ units[0] ]
V_145.length = [ units[1] ]
V_145.amount = [ units[2] ]
V_145.mass = [ units[3] ]
V_145.temperature = [ units[4] ]
V_145.current = [ units[5] ]
V_145.light = [ units[6] ]

# 146
label = variables[146]["label"]
network = variables[146]["network"]
variable_type = variables[146]["type"]
label = variables[146]["label"]
doc = variables[146]["doc"]
onto_ID = "V_146"
V_146 = onto.ProMoVar( onto_ID )
V_146.label = label
V_146.network = network
V_146.variable_type = variable_type
V_146.comment = doc

units = variables[146]["units"].asList()
V_146.time = [ units[0] ]
V_146.length = [ units[1] ]
V_146.amount = [ units[2] ]
V_146.mass = [ units[3] ]
V_146.temperature = [ units[4] ]
V_146.current = [ units[5] ]
V_146.light = [ units[6] ]

# 147
label = variables[147]["label"]
network = variables[147]["network"]
variable_type = variables[147]["type"]
label = variables[147]["label"]
doc = variables[147]["doc"]
onto_ID = "V_147"
V_147 = onto.ProMoVar( onto_ID )
V_147.label = label
V_147.network = network
V_147.variable_type = variable_type
V_147.comment = doc

units = variables[147]["units"].asList()
V_147.time = [ units[0] ]
V_147.length = [ units[1] ]
V_147.amount = [ units[2] ]
V_147.mass = [ units[3] ]
V_147.temperature = [ units[4] ]
V_147.current = [ units[5] ]
V_147.light = [ units[6] ]

# 151
label = variables[151]["label"]
network = variables[151]["network"]
variable_type = variables[151]["type"]
label = variables[151]["label"]
doc = variables[151]["doc"]
onto_ID = "V_151"
V_151 = onto.ProMoVar( onto_ID )
V_151.label = label
V_151.network = network
V_151.variable_type = variable_type
V_151.comment = doc

units = variables[151]["units"].asList()
V_151.time = [ units[0] ]
V_151.length = [ units[1] ]
V_151.amount = [ units[2] ]
V_151.mass = [ units[3] ]
V_151.temperature = [ units[4] ]
V_151.current = [ units[5] ]
V_151.light = [ units[6] ]

# 152
label = variables[152]["label"]
network = variables[152]["network"]
variable_type = variables[152]["type"]
label = variables[152]["label"]
doc = variables[152]["doc"]
onto_ID = "V_152"
V_152 = onto.ProMoVar( onto_ID )
V_152.label = label
V_152.network = network
V_152.variable_type = variable_type
V_152.comment = doc

units = variables[152]["units"].asList()
V_152.time = [ units[0] ]
V_152.length = [ units[1] ]
V_152.amount = [ units[2] ]
V_152.mass = [ units[3] ]
V_152.temperature = [ units[4] ]
V_152.current = [ units[5] ]
V_152.light = [ units[6] ]

# 153
label = variables[153]["label"]
network = variables[153]["network"]
variable_type = variables[153]["type"]
label = variables[153]["label"]
doc = variables[153]["doc"]
onto_ID = "V_153"
V_153 = onto.ProMoVar( onto_ID )
V_153.label = label
V_153.network = network
V_153.variable_type = variable_type
V_153.comment = doc

units = variables[153]["units"].asList()
V_153.time = [ units[0] ]
V_153.length = [ units[1] ]
V_153.amount = [ units[2] ]
V_153.mass = [ units[3] ]
V_153.temperature = [ units[4] ]
V_153.current = [ units[5] ]
V_153.light = [ units[6] ]

# 154
label = variables[154]["label"]
network = variables[154]["network"]
variable_type = variables[154]["type"]
label = variables[154]["label"]
doc = variables[154]["doc"]
onto_ID = "V_154"
V_154 = onto.ProMoVar( onto_ID )
V_154.label = label
V_154.network = network
V_154.variable_type = variable_type
V_154.comment = doc

units = variables[154]["units"].asList()
V_154.time = [ units[0] ]
V_154.length = [ units[1] ]
V_154.amount = [ units[2] ]
V_154.mass = [ units[3] ]
V_154.temperature = [ units[4] ]
V_154.current = [ units[5] ]
V_154.light = [ units[6] ]

# 155
label = variables[155]["label"]
network = variables[155]["network"]
variable_type = variables[155]["type"]
label = variables[155]["label"]
doc = variables[155]["doc"]
onto_ID = "V_155"
V_155 = onto.ProMoVar( onto_ID )
V_155.label = label
V_155.network = network
V_155.variable_type = variable_type
V_155.comment = doc

units = variables[155]["units"].asList()
V_155.time = [ units[0] ]
V_155.length = [ units[1] ]
V_155.amount = [ units[2] ]
V_155.mass = [ units[3] ]
V_155.temperature = [ units[4] ]
V_155.current = [ units[5] ]
V_155.light = [ units[6] ]

# 157
label = variables[157]["label"]
network = variables[157]["network"]
variable_type = variables[157]["type"]
label = variables[157]["label"]
doc = variables[157]["doc"]
onto_ID = "V_157"
V_157 = onto.ProMoVar( onto_ID )
V_157.label = label
V_157.network = network
V_157.variable_type = variable_type
V_157.comment = doc

units = variables[157]["units"].asList()
V_157.time = [ units[0] ]
V_157.length = [ units[1] ]
V_157.amount = [ units[2] ]
V_157.mass = [ units[3] ]
V_157.temperature = [ units[4] ]
V_157.current = [ units[5] ]
V_157.light = [ units[6] ]

# 158
label = variables[158]["label"]
network = variables[158]["network"]
variable_type = variables[158]["type"]
label = variables[158]["label"]
doc = variables[158]["doc"]
onto_ID = "V_158"
V_158 = onto.ProMoVar( onto_ID )
V_158.label = label
V_158.network = network
V_158.variable_type = variable_type
V_158.comment = doc

units = variables[158]["units"].asList()
V_158.time = [ units[0] ]
V_158.length = [ units[1] ]
V_158.amount = [ units[2] ]
V_158.mass = [ units[3] ]
V_158.temperature = [ units[4] ]
V_158.current = [ units[5] ]
V_158.light = [ units[6] ]

# 159
label = variables[159]["label"]
network = variables[159]["network"]
variable_type = variables[159]["type"]
label = variables[159]["label"]
doc = variables[159]["doc"]
onto_ID = "V_159"
V_159 = onto.ProMoVar( onto_ID )
V_159.label = label
V_159.network = network
V_159.variable_type = variable_type
V_159.comment = doc

units = variables[159]["units"].asList()
V_159.time = [ units[0] ]
V_159.length = [ units[1] ]
V_159.amount = [ units[2] ]
V_159.mass = [ units[3] ]
V_159.temperature = [ units[4] ]
V_159.current = [ units[5] ]
V_159.light = [ units[6] ]

# 160
label = variables[160]["label"]
network = variables[160]["network"]
variable_type = variables[160]["type"]
label = variables[160]["label"]
doc = variables[160]["doc"]
onto_ID = "V_160"
V_160 = onto.ProMoVar( onto_ID )
V_160.label = label
V_160.network = network
V_160.variable_type = variable_type
V_160.comment = doc

units = variables[160]["units"].asList()
V_160.time = [ units[0] ]
V_160.length = [ units[1] ]
V_160.amount = [ units[2] ]
V_160.mass = [ units[3] ]
V_160.temperature = [ units[4] ]
V_160.current = [ units[5] ]
V_160.light = [ units[6] ]

# 162
label = variables[162]["label"]
network = variables[162]["network"]
variable_type = variables[162]["type"]
label = variables[162]["label"]
doc = variables[162]["doc"]
onto_ID = "V_162"
V_162 = onto.ProMoVar( onto_ID )
V_162.label = label
V_162.network = network
V_162.variable_type = variable_type
V_162.comment = doc

units = variables[162]["units"].asList()
V_162.time = [ units[0] ]
V_162.length = [ units[1] ]
V_162.amount = [ units[2] ]
V_162.mass = [ units[3] ]
V_162.temperature = [ units[4] ]
V_162.current = [ units[5] ]
V_162.light = [ units[6] ]

# 163
label = variables[163]["label"]
network = variables[163]["network"]
variable_type = variables[163]["type"]
label = variables[163]["label"]
doc = variables[163]["doc"]
onto_ID = "V_163"
V_163 = onto.ProMoVar( onto_ID )
V_163.label = label
V_163.network = network
V_163.variable_type = variable_type
V_163.comment = doc

units = variables[163]["units"].asList()
V_163.time = [ units[0] ]
V_163.length = [ units[1] ]
V_163.amount = [ units[2] ]
V_163.mass = [ units[3] ]
V_163.temperature = [ units[4] ]
V_163.current = [ units[5] ]
V_163.light = [ units[6] ]

# 164
label = variables[164]["label"]
network = variables[164]["network"]
variable_type = variables[164]["type"]
label = variables[164]["label"]
doc = variables[164]["doc"]
onto_ID = "V_164"
V_164 = onto.ProMoVar( onto_ID )
V_164.label = label
V_164.network = network
V_164.variable_type = variable_type
V_164.comment = doc

units = variables[164]["units"].asList()
V_164.time = [ units[0] ]
V_164.length = [ units[1] ]
V_164.amount = [ units[2] ]
V_164.mass = [ units[3] ]
V_164.temperature = [ units[4] ]
V_164.current = [ units[5] ]
V_164.light = [ units[6] ]

# functions assignments

#1

V_1.has_function = []
#2

V_2.has_function = []
incidence_list = []
incidence_list.append( V_1 )
incidence_list.append( V_1 )
F_ID = "F_1"
F_1 = onto.function( F_ID )
F_1.is_function_of = incidence_list
V_2.has_function.append( F_1 )
#3

V_3.has_function = []
incidence_list = []
incidence_list.append( V_1 )
incidence_list.append( V_1 )
F_ID = "F_2"
F_2 = onto.function( F_ID )
F_2.is_function_of = incidence_list
V_3.has_function.append( F_2 )
#4

V_4.has_function = []
incidence_list = []
incidence_list.append( V_1 )
incidence_list.append( V_1 )
F_ID = "F_3"
F_3 = onto.function( F_ID )
F_3.is_function_of = incidence_list
V_4.has_function.append( F_3 )
#5

V_5.has_function = []
#6

V_6.has_function = []
incidence_list = []
incidence_list.append( V_5 )
incidence_list.append( V_1 )
F_ID = "F_4"
F_4 = onto.function( F_ID )
F_4.is_function_of = incidence_list
V_6.has_function.append( F_4 )
#7

V_7.has_function = []
incidence_list = []
incidence_list.append( V_5 )
incidence_list.append( V_1 )
F_ID = "F_5"
F_5 = onto.function( F_ID )
F_5.is_function_of = incidence_list
V_7.has_function.append( F_5 )
#8

V_8.has_function = []
#9

V_9.has_function = []
#10

V_10.has_function = []
#11

V_11.has_function = []
#12

V_12.has_function = []
#13

V_13.has_function = []
#14

V_14.has_function = []
#15

V_15.has_function = []
#16

V_16.has_function = []
incidence_list = []
incidence_list.append( V_101 )
incidence_list.append( V_5 )
incidence_list.append( V_6 )
incidence_list.append( V_7 )
F_ID = "F_86"
F_86 = onto.function( F_ID )
F_86.is_function_of = incidence_list
V_16.has_function.append( F_86 )
#17

V_17.has_function = []
incidence_list = []
incidence_list.append( V_13 )
incidence_list.append( V_15 )
F_ID = "F_6"
F_6 = onto.function( F_ID )
F_6.is_function_of = incidence_list
V_17.has_function.append( F_6 )
#18

V_18.has_function = []
incidence_list = []
incidence_list.append( V_13 )
incidence_list.append( V_14 )
F_ID = "F_7"
F_7 = onto.function( F_ID )
F_7.is_function_of = incidence_list
V_18.has_function.append( F_7 )
#19

V_19.has_function = []
incidence_list = []
incidence_list.append( V_13 )
incidence_list.append( V_16 )
F_ID = "F_8"
F_8 = onto.function( F_ID )
F_8.is_function_of = incidence_list
V_19.has_function.append( F_8 )
#20

V_20.has_function = []
incidence_list = []
incidence_list.append( V_13 )
incidence_list.append( V_17 )
incidence_list.append( V_15 )
F_ID = "F_9"
F_9 = onto.function( F_ID )
F_9.is_function_of = incidence_list
V_20.has_function.append( F_9 )
incidence_list = []
incidence_list.append( V_108 )
incidence_list.append( V_5 )
incidence_list.append( V_6 )
incidence_list.append( V_7 )
F_ID = "F_87"
F_87 = onto.function( F_ID )
F_87.is_function_of = incidence_list
V_20.has_function.append( F_87 )
#21

V_21.has_function = []
incidence_list = []
incidence_list.append( V_13 )
incidence_list.append( V_18 )
incidence_list.append( V_14 )
F_ID = "F_10"
F_10 = onto.function( F_ID )
F_10.is_function_of = incidence_list
V_21.has_function.append( F_10 )
#22

V_22.has_function = []
incidence_list = []
incidence_list.append( V_13 )
incidence_list.append( V_17 )
incidence_list.append( V_15 )
incidence_list.append( V_18 )
incidence_list.append( V_14 )
F_ID = "F_11"
F_11 = onto.function( F_ID )
F_11.is_function_of = incidence_list
V_22.has_function.append( F_11 )
#23

V_23.has_function = []
#24

V_24.has_function = []
#27

V_27.has_function = []
incidence_list = []
incidence_list.append( V_23 )
incidence_list.append( V_13 )
F_ID = "F_14"
F_14 = onto.function( F_ID )
F_14.is_function_of = incidence_list
V_27.has_function.append( F_14 )
incidence_list = []
incidence_list.append( V_117 )
incidence_list.append( V_113 )
F_ID = "F_95"
F_95 = onto.function( F_ID )
F_95.is_function_of = incidence_list
V_27.has_function.append( F_95 )
#28

V_28.has_function = []
incidence_list = []
incidence_list.append( V_10 )
incidence_list.append( V_5 )
F_ID = "F_15"
F_15 = onto.function( F_ID )
F_15.is_function_of = incidence_list
V_28.has_function.append( F_15 )
#29

V_29.has_function = []
incidence_list = []
incidence_list.append( V_11 )
incidence_list.append( V_5 )
F_ID = "F_16"
F_16 = onto.function( F_ID )
F_16.is_function_of = incidence_list
V_29.has_function.append( F_16 )
#30

V_30.has_function = []
incidence_list = []
incidence_list.append( V_12 )
incidence_list.append( V_5 )
F_ID = "F_17"
F_17 = onto.function( F_ID )
F_17.is_function_of = incidence_list
V_30.has_function.append( F_17 )
#32

V_32.has_function = []
#33

V_33.has_function = []
#34

V_34.has_function = []
#35

V_35.has_function = []
#36

V_36.has_function = []
#37

V_37.has_function = []
#38

V_38.has_function = []
#40

V_40.has_function = []
#41

V_41.has_function = []
incidence_list = []
incidence_list.append( V_40 )
F_ID = "F_20"
F_20 = onto.function( F_ID )
F_20.is_function_of = incidence_list
V_41.has_function.append( F_20 )
#42

V_42.has_function = []
incidence_list = []
incidence_list.append( V_20 )
incidence_list.append( V_18 )
F_ID = "F_21"
F_21 = onto.function( F_ID )
F_21.is_function_of = incidence_list
V_42.has_function.append( F_21 )
#43

V_43.has_function = []
incidence_list = []
incidence_list.append( V_13 )
incidence_list.append( V_18 )
F_ID = "F_22"
F_22 = onto.function( F_ID )
F_22.is_function_of = incidence_list
V_43.has_function.append( F_22 )
#44

V_44.has_function = []
incidence_list = []
incidence_list.append( V_15 )
incidence_list.append( V_13 )
incidence_list.append( V_18 )
incidence_list.append( V_28 )
F_ID = "F_23"
F_23 = onto.function( F_ID )
F_23.is_function_of = incidence_list
V_44.has_function.append( F_23 )
#45

V_45.has_function = []
incidence_list = []
incidence_list.append( V_15 )
incidence_list.append( V_13 )
incidence_list.append( V_18 )
incidence_list.append( V_29 )
F_ID = "F_24"
F_24 = onto.function( F_ID )
F_24.is_function_of = incidence_list
V_45.has_function.append( F_24 )
#46

V_46.has_function = []
incidence_list = []
incidence_list.append( V_15 )
incidence_list.append( V_13 )
incidence_list.append( V_18 )
incidence_list.append( V_30 )
F_ID = "F_25"
F_25 = onto.function( F_ID )
F_25.is_function_of = incidence_list
V_46.has_function.append( F_25 )
#47

V_47.has_function = []
incidence_list = []
incidence_list.append( V_44 )
incidence_list.append( V_45 )
incidence_list.append( V_46 )
F_ID = "F_26"
F_26 = onto.function( F_ID )
F_26.is_function_of = incidence_list
V_47.has_function.append( F_26 )
#48

V_48.has_function = []
incidence_list = []
incidence_list.append( V_40 )
incidence_list.append( V_19 )
incidence_list.append( V_15 )
incidence_list.append( V_13 )
incidence_list.append( V_17 )
incidence_list.append( V_28 )
F_ID = "F_27"
F_27 = onto.function( F_ID )
F_27.is_function_of = incidence_list
V_48.has_function.append( F_27 )
#49

V_49.has_function = []
incidence_list = []
incidence_list.append( V_40 )
incidence_list.append( V_19 )
incidence_list.append( V_15 )
incidence_list.append( V_13 )
incidence_list.append( V_17 )
incidence_list.append( V_29 )
F_ID = "F_28"
F_28 = onto.function( F_ID )
F_28.is_function_of = incidence_list
V_49.has_function.append( F_28 )
#50

V_50.has_function = []
incidence_list = []
incidence_list.append( V_40 )
incidence_list.append( V_19 )
incidence_list.append( V_15 )
incidence_list.append( V_13 )
incidence_list.append( V_17 )
incidence_list.append( V_30 )
F_ID = "F_29"
F_29 = onto.function( F_ID )
F_29.is_function_of = incidence_list
V_50.has_function.append( F_29 )
#51

V_51.has_function = []
incidence_list = []
incidence_list.append( V_48 )
incidence_list.append( V_49 )
incidence_list.append( V_50 )
F_ID = "F_30"
F_30 = onto.function( F_ID )
F_30.is_function_of = incidence_list
V_51.has_function.append( F_30 )
#52

V_52.has_function = []
incidence_list = []
incidence_list.append( V_19 )
incidence_list.append( V_28 )
incidence_list.append( V_15 )
incidence_list.append( V_13 )
incidence_list.append( V_19 )
F_ID = "F_31"
F_31 = onto.function( F_ID )
F_31.is_function_of = incidence_list
V_52.has_function.append( F_31 )
#53

V_53.has_function = []
incidence_list = []
incidence_list.append( V_19 )
incidence_list.append( V_29 )
incidence_list.append( V_15 )
incidence_list.append( V_13 )
incidence_list.append( V_19 )
F_ID = "F_32"
F_32 = onto.function( F_ID )
F_32.is_function_of = incidence_list
V_53.has_function.append( F_32 )
#54

V_54.has_function = []
incidence_list = []
incidence_list.append( V_19 )
incidence_list.append( V_30 )
incidence_list.append( V_15 )
incidence_list.append( V_13 )
incidence_list.append( V_19 )
F_ID = "F_33"
F_33 = onto.function( F_ID )
F_33.is_function_of = incidence_list
V_54.has_function.append( F_33 )
#55

V_55.has_function = []
incidence_list = []
incidence_list.append( V_52 )
incidence_list.append( V_53 )
incidence_list.append( V_54 )
F_ID = "F_34"
F_34 = onto.function( F_ID )
F_34.is_function_of = incidence_list
V_55.has_function.append( F_34 )
#56

V_56.has_function = []
incidence_list = []
incidence_list.append( V_20 )
incidence_list.append( V_16 )
F_ID = "F_35"
F_35 = onto.function( F_ID )
F_35.is_function_of = incidence_list
V_56.has_function.append( F_35 )
#57

V_57.has_function = []
incidence_list = []
incidence_list.append( V_41 )
incidence_list.append( V_16 )
F_ID = "F_36"
F_36 = onto.function( F_ID )
F_36.is_function_of = incidence_list
V_57.has_function.append( F_36 )
#58

V_58.has_function = []
incidence_list = []
incidence_list.append( V_57 )
F_ID = "F_37"
F_37 = onto.function( F_ID )
F_37.is_function_of = incidence_list
V_58.has_function.append( F_37 )
#59

V_59.has_function = []
incidence_list = []
incidence_list.append( V_58 )
incidence_list.append( V_15 )
F_ID = "F_38"
F_38 = onto.function( F_ID )
F_38.is_function_of = incidence_list
V_59.has_function.append( F_38 )
#60

V_60.has_function = []
incidence_list = []
incidence_list.append( V_35 )
incidence_list.append( V_18 )
F_ID = "F_39"
F_39 = onto.function( F_ID )
F_39.is_function_of = incidence_list
V_60.has_function.append( F_39 )
#62

V_62.has_function = []
incidence_list = []
incidence_list.append( V_157 )
incidence_list.append( V_60 )
incidence_list.append( V_1 )
F_ID = "F_41"
F_41 = onto.function( F_ID )
F_41.is_function_of = incidence_list
V_62.has_function.append( F_41 )
#63

V_63.has_function = []
incidence_list = []
incidence_list.append( V_38 )
incidence_list.append( V_62 )
incidence_list.append( V_157 )
incidence_list.append( V_60 )
F_ID = "F_42"
F_42 = onto.function( F_ID )
F_42.is_function_of = incidence_list
V_63.has_function.append( F_42 )
#65

V_65.has_function = []
#66

V_66.has_function = []
incidence_list = []
incidence_list.append( V_15 )
incidence_list.append( V_16 )
F_ID = "F_44"
F_44 = onto.function( F_ID )
F_44.is_function_of = incidence_list
V_66.has_function.append( F_44 )
#67

V_67.has_function = []
incidence_list = []
incidence_list.append( V_66 )
F_ID = "F_45"
F_45 = onto.function( F_ID )
F_45.is_function_of = incidence_list
V_67.has_function.append( F_45 )
#70

V_70.has_function = []
#71

V_71.has_function = []
incidence_list = []
incidence_list.append( V_11 )
incidence_list.append( V_12 )
F_ID = "F_48"
F_48 = onto.function( F_ID )
F_48.is_function_of = incidence_list
V_71.has_function.append( F_48 )
#72

V_72.has_function = []
incidence_list = []
incidence_list.append( V_10 )
incidence_list.append( V_12 )
F_ID = "F_49"
F_49 = onto.function( F_ID )
F_49.is_function_of = incidence_list
V_72.has_function.append( F_49 )
#73

V_73.has_function = []
incidence_list = []
incidence_list.append( V_10 )
incidence_list.append( V_11 )
F_ID = "F_50"
F_50 = onto.function( F_ID )
F_50.is_function_of = incidence_list
V_73.has_function.append( F_50 )
#74

V_74.has_function = []
incidence_list = []
incidence_list.append( V_59 )
F_ID = "F_51"
F_51 = onto.function( F_ID )
F_51.is_function_of = incidence_list
V_74.has_function.append( F_51 )
#75

V_75.has_function = []
incidence_list = []
incidence_list.append( V_56 )
F_ID = "F_52"
F_52 = onto.function( F_ID )
F_52.is_function_of = incidence_list
V_75.has_function.append( F_52 )
#76

V_76.has_function = []
incidence_list = []
incidence_list.append( V_44 )
F_ID = "F_53"
F_53 = onto.function( F_ID )
F_53.is_function_of = incidence_list
V_76.has_function.append( F_53 )
#77

V_77.has_function = []
incidence_list = []
incidence_list.append( V_43 )
F_ID = "F_54"
F_54 = onto.function( F_ID )
F_54.is_function_of = incidence_list
V_77.has_function.append( F_54 )
#78

V_78.has_function = []
incidence_list = []
incidence_list.append( V_45 )
F_ID = "F_55"
F_55 = onto.function( F_ID )
F_55.is_function_of = incidence_list
V_78.has_function.append( F_55 )
#79

V_79.has_function = []
incidence_list = []
incidence_list.append( V_46 )
F_ID = "F_56"
F_56 = onto.function( F_ID )
F_56.is_function_of = incidence_list
V_79.has_function.append( F_56 )
#80

V_80.has_function = []
incidence_list = []
incidence_list.append( V_47 )
F_ID = "F_57"
F_57 = onto.function( F_ID )
F_57.is_function_of = incidence_list
V_80.has_function.append( F_57 )
#81

V_81.has_function = []
incidence_list = []
incidence_list.append( V_48 )
F_ID = "F_58"
F_58 = onto.function( F_ID )
F_58.is_function_of = incidence_list
V_81.has_function.append( F_58 )
#82

V_82.has_function = []
incidence_list = []
incidence_list.append( V_42 )
F_ID = "F_59"
F_59 = onto.function( F_ID )
F_59.is_function_of = incidence_list
V_82.has_function.append( F_59 )
#83

V_83.has_function = []
incidence_list = []
incidence_list.append( V_49 )
F_ID = "F_60"
F_60 = onto.function( F_ID )
F_60.is_function_of = incidence_list
V_83.has_function.append( F_60 )
#84

V_84.has_function = []
incidence_list = []
incidence_list.append( V_50 )
F_ID = "F_61"
F_61 = onto.function( F_ID )
F_61.is_function_of = incidence_list
V_84.has_function.append( F_61 )
#85

V_85.has_function = []
incidence_list = []
incidence_list.append( V_51 )
F_ID = "F_62"
F_62 = onto.function( F_ID )
F_62.is_function_of = incidence_list
V_85.has_function.append( F_62 )
#86

V_86.has_function = []
incidence_list = []
incidence_list.append( V_52 )
F_ID = "F_63"
F_63 = onto.function( F_ID )
F_63.is_function_of = incidence_list
V_86.has_function.append( F_63 )
#87

V_87.has_function = []
incidence_list = []
incidence_list.append( V_53 )
F_ID = "F_64"
F_64 = onto.function( F_ID )
F_64.is_function_of = incidence_list
V_87.has_function.append( F_64 )
#88

V_88.has_function = []
incidence_list = []
incidence_list.append( V_54 )
F_ID = "F_65"
F_65 = onto.function( F_ID )
F_65.is_function_of = incidence_list
V_88.has_function.append( F_65 )
#89

V_89.has_function = []
incidence_list = []
incidence_list.append( V_55 )
F_ID = "F_66"
F_66 = onto.function( F_ID )
F_66.is_function_of = incidence_list
V_89.has_function.append( F_66 )
#90

V_90.has_function = []
#91

V_91.has_function = []
#92

V_92.has_function = []
incidence_list = []
incidence_list.append( V_74 )
incidence_list.append( V_81 )
incidence_list.append( V_71 )
incidence_list.append( V_90 )
incidence_list.append( V_17 )
F_ID = "F_67"
F_67 = onto.function( F_ID )
F_67.is_function_of = incidence_list
V_92.has_function.append( F_67 )
#93

V_93.has_function = []
incidence_list = []
incidence_list.append( V_71 )
incidence_list.append( V_86 )
incidence_list.append( V_91 )
incidence_list.append( V_19 )
F_ID = "F_68"
F_68 = onto.function( F_ID )
F_68.is_function_of = incidence_list
V_93.has_function.append( F_68 )
#94

V_94.has_function = []
incidence_list = []
incidence_list.append( V_70 )
incidence_list.append( V_93 )
F_ID = "F_69"
F_69 = onto.function( F_ID )
F_69.is_function_of = incidence_list
V_94.has_function.append( F_69 )
#95

V_95.has_function = []
incidence_list = []
incidence_list.append( V_70 )
incidence_list.append( V_75 )
incidence_list.append( V_93 )
F_ID = "F_70"
F_70 = onto.function( F_ID )
F_70.is_function_of = incidence_list
V_95.has_function.append( F_70 )
#96

V_96.has_function = []
incidence_list = []
incidence_list.append( V_8 )
incidence_list.append( V_95 )
F_ID = "F_71"
F_71 = onto.function( F_ID )
F_71.is_function_of = incidence_list
V_96.has_function.append( F_71 )
#97

V_97.has_function = []
incidence_list = []
incidence_list.append( V_8 )
incidence_list.append( V_17 )
F_ID = "F_72"
F_72 = onto.function( F_ID )
F_72.is_function_of = incidence_list
V_97.has_function.append( F_72 )
#98

V_98.has_function = []
incidence_list = []
incidence_list.append( V_4 )
incidence_list.append( V_70 )
incidence_list.append( V_97 )
incidence_list.append( V_70 )
incidence_list.append( V_66 )
F_ID = "F_73"
F_73 = onto.function( F_ID )
F_73.is_function_of = incidence_list
V_98.has_function.append( F_73 )
#99

V_99.has_function = []
incidence_list = []
incidence_list.append( V_92 )
incidence_list.append( V_98 )
F_ID = "F_74"
F_74 = onto.function( F_ID )
F_74.is_function_of = incidence_list
V_99.has_function.append( F_74 )
#100

V_100.has_function = []
incidence_list = []
incidence_list.append( V_70 )
incidence_list.append( V_99 )
F_ID = "F_75"
F_75 = onto.function( F_ID )
F_75.is_function_of = incidence_list
V_100.has_function.append( F_75 )
#101

V_101.has_function = []
incidence_list = []
incidence_list.append( V_100 )
incidence_list.append( V_94 )
incidence_list.append( V_164 )
F_ID = "F_76"
F_76 = onto.function( F_ID )
F_76.is_function_of = incidence_list
V_101.has_function.append( F_76 )
#102

V_102.has_function = []
incidence_list = []
incidence_list.append( V_70 )
incidence_list.append( V_75 )
incidence_list.append( V_99 )
F_ID = "F_77"
F_77 = onto.function( F_ID )
F_77.is_function_of = incidence_list
V_102.has_function.append( F_77 )
#103

V_103.has_function = []
incidence_list = []
incidence_list.append( V_8 )
incidence_list.append( V_102 )
F_ID = "F_78"
F_78 = onto.function( F_ID )
F_78.is_function_of = incidence_list
V_103.has_function.append( F_78 )
#104

V_104.has_function = []
incidence_list = []
incidence_list.append( V_102 )
incidence_list.append( V_1 )
F_ID = "F_79"
F_79 = onto.function( F_ID )
F_79.is_function_of = incidence_list
V_104.has_function.append( F_79 )
#105

V_105.has_function = []
incidence_list = []
incidence_list.append( V_8 )
incidence_list.append( V_104 )
F_ID = "F_80"
F_80 = onto.function( F_ID )
F_80.is_function_of = incidence_list
V_105.has_function.append( F_80 )
#106

V_106.has_function = []
incidence_list = []
incidence_list.append( V_71 )
incidence_list.append( V_76 )
incidence_list.append( V_90 )
incidence_list.append( V_18 )
F_ID = "F_81"
F_81 = onto.function( F_ID )
F_81.is_function_of = incidence_list
V_106.has_function.append( F_81 )
#107

V_107.has_function = []
incidence_list = []
incidence_list.append( V_8 )
incidence_list.append( V_106 )
F_ID = "F_82"
F_82 = onto.function( F_ID )
F_82.is_function_of = incidence_list
V_107.has_function.append( F_82 )
#108

V_108.has_function = []
incidence_list = []
incidence_list.append( V_103 )
incidence_list.append( V_96 )
incidence_list.append( V_107 )
incidence_list.append( V_105 )
F_ID = "F_83"
F_83 = onto.function( F_ID )
F_83.is_function_of = incidence_list
V_108.has_function.append( F_83 )
#109

V_109.has_function = []
incidence_list = []
incidence_list.append( V_20 )
incidence_list.append( V_1 )
F_ID = "F_84"
F_84 = onto.function( F_ID )
F_84.is_function_of = incidence_list
V_109.has_function.append( F_84 )
#110

V_110.has_function = []
incidence_list = []
incidence_list.append( V_16 )
incidence_list.append( V_1 )
F_ID = "F_85"
F_85 = onto.function( F_ID )
F_85.is_function_of = incidence_list
V_110.has_function.append( F_85 )
#112

V_112.has_function = []
incidence_list = []
incidence_list.append( V_112 )
incidence_list.append( V_1 )
F_ID = "F_88"
F_88 = onto.function( F_ID )
F_88.is_function_of = incidence_list
V_112.has_function.append( F_88 )
#113

V_113.has_function = []
incidence_list = []
incidence_list.append( V_23 )
incidence_list.append( V_5 )
F_ID = "F_89"
F_89 = onto.function( F_ID )
F_89.is_function_of = incidence_list
V_113.has_function.append( F_89 )
#114

V_114.has_function = []
incidence_list = []
incidence_list.append( V_113 )
F_ID = "F_90"
F_90 = onto.function( F_ID )
F_90.is_function_of = incidence_list
V_114.has_function.append( F_90 )
#115

V_115.has_function = []
incidence_list = []
incidence_list.append( V_114 )
incidence_list.append( V_27 )
F_ID = "F_91"
F_91 = onto.function( F_ID )
F_91.is_function_of = incidence_list
V_115.has_function.append( F_91 )
incidence_list = []
incidence_list.append( V_115 )
incidence_list.append( V_1 )
F_ID = "F_92"
F_92 = onto.function( F_ID )
F_92.is_function_of = incidence_list
V_115.has_function.append( F_92 )
#116

V_116.has_function = []
incidence_list = []
incidence_list.append( V_115 )
incidence_list.append( V_112 )
F_ID = "F_93"
F_93 = onto.function( F_ID )
F_93.is_function_of = incidence_list
V_116.has_function.append( F_93 )
#117

V_117.has_function = []
incidence_list = []
incidence_list.append( V_116 )
F_ID = "F_94"
F_94 = onto.function( F_ID )
F_94.is_function_of = incidence_list
V_117.has_function.append( F_94 )
#118

V_118.has_function = []
incidence_list = []
incidence_list.append( V_2 )
incidence_list.append( V_27 )
F_ID = "F_96"
F_96 = onto.function( F_ID )
F_96.is_function_of = incidence_list
V_118.has_function.append( F_96 )
incidence_list = []
incidence_list.append( V_27 )
F_ID = "F_97"
F_97 = onto.function( F_ID )
F_97.is_function_of = incidence_list
V_118.has_function.append( F_97 )
incidence_list = []
incidence_list.append( V_118 )
incidence_list.append( V_3 )
F_ID = "F_98"
F_98 = onto.function( F_ID )
F_98.is_function_of = incidence_list
V_118.has_function.append( F_98 )
#119

V_119.has_function = []
incidence_list = []
incidence_list.append( V_113 )
F_ID = "F_99"
F_99 = onto.function( F_ID )
F_99.is_function_of = incidence_list
V_119.has_function.append( F_99 )
#124

V_124.has_function = []
incidence_list = []
incidence_list.append( V_112 )
F_ID = "F_104"
F_104 = onto.function( F_ID )
F_104.is_function_of = incidence_list
V_124.has_function.append( F_104 )
#125

V_125.has_function = []
incidence_list = []
incidence_list.append( V_18 )
F_ID = "F_105"
F_105 = onto.function( F_ID )
F_105.is_function_of = incidence_list
V_125.has_function.append( F_105 )
#126

V_126.has_function = []
incidence_list = []
incidence_list.append( V_17 )
incidence_list.append( V_18 )
incidence_list.append( V_19 )
incidence_list.append( V_66 )
incidence_list.append( V_27 )
F_ID = "F_106"
F_106 = onto.function( F_ID )
F_106.is_function_of = incidence_list
V_126.has_function.append( F_106 )
#127

V_127.has_function = []
#128

V_128.has_function = []
incidence_list = []
incidence_list.append( V_127 )
incidence_list.append( V_16 )
F_ID = "F_107"
F_107 = onto.function( F_ID )
F_107.is_function_of = incidence_list
V_128.has_function.append( F_107 )
#129

V_129.has_function = []
#130

V_130.has_function = []
#131

V_131.has_function = []
#132

V_132.has_function = []
#133

V_133.has_function = []
incidence_list = []
incidence_list.append( V_133 )
incidence_list.append( V_1 )
F_ID = "F_119"
F_119 = onto.function( F_ID )
F_119.is_function_of = incidence_list
V_133.has_function.append( F_119 )
#134

V_134.has_function = []
#135

V_135.has_function = []
incidence_list = []
incidence_list.append( V_134 )
incidence_list.append( V_133 )
F_ID = "F_108"
F_108 = onto.function( F_ID )
F_108.is_function_of = incidence_list
V_135.has_function.append( F_108 )
#136

V_136.has_function = []
incidence_list = []
incidence_list.append( V_139 )
incidence_list.append( V_138 )
incidence_list.append( V_5 )
incidence_list.append( V_6 )
incidence_list.append( V_7 )
F_ID = "F_111"
F_111 = onto.function( F_ID )
F_111.is_function_of = incidence_list
V_136.has_function.append( F_111 )
#137

V_137.has_function = []
incidence_list = []
incidence_list.append( V_136 )
incidence_list.append( V_1 )
F_ID = "F_109"
F_109 = onto.function( F_ID )
F_109.is_function_of = incidence_list
V_137.has_function.append( F_109 )
#138

V_138.has_function = []
incidence_list = []
incidence_list.append( V_129 )
incidence_list.append( V_136 )
incidence_list.append( V_130 )
incidence_list.append( V_135 )
F_ID = "F_110"
F_110 = onto.function( F_ID )
F_110.is_function_of = incidence_list
V_138.has_function.append( F_110 )
#139

V_139.has_function = []
#140

V_140.has_function = []
incidence_list = []
incidence_list.append( V_112 )
F_ID = "F_112"
F_112 = onto.function( F_ID )
F_112.is_function_of = incidence_list
V_140.has_function.append( F_112 )
#141

V_141.has_function = []
incidence_list = []
incidence_list.append( V_119 )
F_ID = "F_113"
F_113 = onto.function( F_ID )
F_113.is_function_of = incidence_list
V_141.has_function.append( F_113 )
#142

V_142.has_function = []
incidence_list = []
incidence_list.append( V_27 )
F_ID = "F_114"
F_114 = onto.function( F_ID )
F_114.is_function_of = incidence_list
V_142.has_function.append( F_114 )
#143

V_143.has_function = []
incidence_list = []
incidence_list.append( V_142 )
F_ID = "F_115"
F_115 = onto.function( F_ID )
F_115.is_function_of = incidence_list
V_143.has_function.append( F_115 )
#144

V_144.has_function = []
incidence_list = []
incidence_list.append( V_124 )
F_ID = "F_116"
F_116 = onto.function( F_ID )
F_116.is_function_of = incidence_list
V_144.has_function.append( F_116 )
#145

V_145.has_function = []
incidence_list = []
incidence_list.append( V_141 )
incidence_list.append( V_143 )
F_ID = "F_117"
F_117 = onto.function( F_ID )
F_117.is_function_of = incidence_list
V_145.has_function.append( F_117 )
#146

V_146.has_function = []
incidence_list = []
incidence_list.append( V_141 )
incidence_list.append( V_143 )
incidence_list.append( V_145 )
incidence_list.append( V_144 )
F_ID = "F_118"
F_118 = onto.function( F_ID )
F_118.is_function_of = incidence_list
V_146.has_function.append( F_118 )
#147

V_147.has_function = []
#151

V_151.has_function = []
incidence_list = []
incidence_list.append( V_147 )
incidence_list.append( V_36 )
incidence_list.append( V_67 )
F_ID = "F_123"
F_123 = onto.function( F_ID )
F_123.is_function_of = incidence_list
V_151.has_function.append( F_123 )
#152

V_152.has_function = []
incidence_list = []
incidence_list.append( V_151 )
incidence_list.append( V_1 )
F_ID = "F_124"
F_124 = onto.function( F_ID )
F_124.is_function_of = incidence_list
V_152.has_function.append( F_124 )
#153

V_153.has_function = []
incidence_list = []
incidence_list.append( V_152 )
incidence_list.append( V_151 )
F_ID = "F_125"
F_125 = onto.function( F_ID )
F_125.is_function_of = incidence_list
V_153.has_function.append( F_125 )
#154

V_154.has_function = []
incidence_list = []
incidence_list.append( V_131 )
incidence_list.append( V_136 )
incidence_list.append( V_132 )
incidence_list.append( V_135 )
F_ID = "F_126"
F_126 = onto.function( F_ID )
F_126.is_function_of = incidence_list
V_154.has_function.append( F_126 )
#155

V_155.has_function = []
#157

V_157.has_function = []
incidence_list = []
incidence_list.append( V_24 )
incidence_list.append( V_155 )
F_ID = "F_127"
F_127 = onto.function( F_ID )
F_127.is_function_of = incidence_list
V_157.has_function.append( F_127 )
#158

V_158.has_function = []
#159

V_159.has_function = []
incidence_list = []
incidence_list.append( V_33 )
incidence_list.append( V_158 )
F_ID = "F_128"
F_128 = onto.function( F_ID )
F_128.is_function_of = incidence_list
V_159.has_function.append( F_128 )
#160

V_160.has_function = []
incidence_list = []
incidence_list.append( V_153 )
incidence_list.append( V_159 )
F_ID = "F_129"
F_129 = onto.function( F_ID )
F_129.is_function_of = incidence_list
V_160.has_function.append( F_129 )
#162

V_162.has_function = []
#163

V_163.has_function = []
incidence_list = []
incidence_list.append( V_15 )
incidence_list.append( V_35 )
incidence_list.append( V_63 )
incidence_list.append( V_160 )
incidence_list.append( V_36 )
incidence_list.append( V_159 )
F_ID = "F_130"
F_130 = onto.function( F_ID )
F_130.is_function_of = incidence_list
V_163.has_function.append( F_130 )
#164

V_164.has_function = []
incidence_list = []
incidence_list.append( V_163 )
F_ID = "F_131"
F_131 = onto.function( F_ID )
F_131.is_function_of = incidence_list
V_164.has_function.append( F_131 )

onto.save("variables.ttl", format="ntriples")
