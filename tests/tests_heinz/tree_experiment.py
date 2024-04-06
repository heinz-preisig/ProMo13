import os
import sys

root = os.path.abspath(os.path.join(".."))
sys.path.extend([root, os.path.join(root, 'packages'), os.path.join(root, 'tasks')])

from Common.ontology_container import OntologyContainer
from OntologyBuilder.OntologyEquationEditor.resources import DotGraphVariableEquations

if __name__ == '__main__':
  ontology_name = "HAP_Ontology_Repository-playground_v8"


  ontology_container = OntologyContainer(ontology_name)
  variables = ontology_container.variables
  indices = ontology_container.indices

  # make_variable_equation_pngs(variables, ontology_name)

  dot = DotGraphVariableEquations(variables, indices, 10, ontology_name)

  print("finished")
