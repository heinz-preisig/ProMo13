# pylint: skip-file
import os
import sys

from PyQt5 import QtWidgets

sys.path.insert(0, os.path.abspath("../.."))

from packages.Common.classes.io import load_equations_from_file
from packages.Common.classes.io import load_entities_from_old_file

from packages.OntologyBuilder.BehaviourAssociation import ui_equation_selector_dialog_impl
from packages.OntologyBuilder.BehaviourAssociation import ctrl_equation_selector_dialog

# path_repository = os.path.abspath("../../../../Ontology_Repository")
# path_ontology = "/".join([path_repository, "ProMo_sandbox6-main"])
# path_equations = "/".join([path_ontology, "equations_global_ID.json"])
# path_entities = "/".join([
#   path_ontology,
#   "variable_assignment_to_entity_object.json"
# ])

ontology_name = "ProMo_sandbox6-main"

all_eq = load_equations_from_file(ontology_name)
ent_name = "macroscopic.node.event|lumped|mass.test"
test_entity = load_entities_from_old_file(
        ontology_name,
        all_eq,
        [ent_name],
        )

# print(json.dumps(test_entity[ent_name], cls=EntityJSONEncoder, indent=2))

controller = ctrl_equation_selector_dialog.ControllerEquationSelectorDlg(
        test_entity[ent_name],
        ontology_name
        )

app = QtWidgets.QApplication(sys.argv)
dlg = ui_equation_selector_dialog_impl.EquationSelectorDlg(controller, None)

return_value = dlg.exec_()
if return_value == QtWidgets.QDialog.Accepted:
  print("Accepted")
else:
  print("Cancelled")
