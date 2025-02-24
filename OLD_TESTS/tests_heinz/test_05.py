
import os
import sys

ProMo_path = os.path.join("../../../", "ProMo")
root = os.path.abspath(ProMo_path)

ext = [root, os.path.join(root, 'packages'), \
             os.path.join(root, 'tasks'), \
             os.path.join(root, 'packages', '../../packages/OntologyBuilder', 'EMMO_Integration')
       ]

sys.path.extend(ext)

# from OntologyBuilder.EMMO_Integration.emmo_attach import ProMoOwlOntology
# from OntologyBuilder.OntologyEquationEditor.emmo_attach import ProMoOwlOntology
from OntologyBuilder.EMMO_Integration.emmo_attach import ProMoOwlOntology
# from OntologyBuilder.OntologyEquationEditor.define_equation_ontology import ProMoOwlOntology
from Common.ontology_container import OntologyContainer
from owlready2 import *

ontology = OntologyContainer("ProMo_sandbox8")

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

print("got here")

onto.save("gugus.ttl","ntriples")