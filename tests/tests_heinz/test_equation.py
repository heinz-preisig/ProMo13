# pylint: skip-file
import json
import os
import sys

sys.path.insert(0, os.path.abspath("../../../../"))
from packages.Common.classes import io

path_repository = os.path.abspath("../../../../Ontology_Repository")
path_ontology = "/".join([path_repository, "ProMo_sandbox6-main"])
path_equations = "/".join([path_ontology, "equations_global_ID.json"])
equations = io.load_equations_from_file(path_equations, ["E_2", "E_5", "E_9"])
print(json.dumps(equations, cls=io.EquationJSONEncoder, indent=2))