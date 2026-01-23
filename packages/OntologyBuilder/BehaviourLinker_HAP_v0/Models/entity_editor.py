# In OntologyBuilder/BehaviourLinker_HAP_v0/Models/entity_editor.py

from typing import Optional, Dict, List, Any
from PyQt5 import QtCore
from Common.classes import entity, variable, equation
from OntologyBuilder.BehaviourLinker_HAP_v0.Models import image_list
from OntologyBuilder.BehaviourLinker_HAP_v0.Models.variable_editor import VariableEditorModel


class EntityEditorModel(QtCore.QObject):
    variableChecked = QtCore.pyqtSignal(bool)

    def __init__(
            self,
            editing_entity: 'entity.Entity',
            all_variables: Dict[str, variable.Variable],
            all_equations: Dict[str, equation.Equation],
            is_variant: bool = False,
            variant_source: Optional['entity.Entity'] = None
            ):
        super().__init__()
        self.is_variant = is_variant
        self.variant_source = variant_source
        # Rest of the __init__ method...

        if is_variant and variant_source:
            # Create a variant of the source entity
            self.editing_entity = variant_source.create_variant(editing_entity.entity_name)
        else:
            # Create a new instance
            self.editing_entity = editing_entity

        self.all_variables = all_variables
        self.all_equations = all_equations
        self.variables_model = image_list.ImageListModel()
        self.equations_model = image_list.ImageListModel()
        self.view_all = True

        self.update_variables_model()
        self.update_equations_model()


    def on_view_all_changed(self, view_all: bool):
        self.view_all = view_all
        self.update_variables_model()

    def update_variables_model(self):
        print("\n=== DEBUG: update_variables_model ===")
        print(f"All variables count: {len(self.all_variables)}")
        print(f"View all: {self.view_all}")

        # Get variable IDs from entity
        entity_variable_ids = self.editing_entity.get_variables()
        pending_variable_ids = self.editing_entity.get_pending_vars()

        print(f"Entity variables (IDs): {entity_variable_ids}")
        print(f"Pending variables (IDs): {pending_variable_ids}")

        # Convert variable IDs to actual variable objects
        entity_variables = []
        pending_variables = []

        # Only show variables that are part of the entity's type definition
        if entity_variable_ids:
            # If we have entity variables, show them
            entity_variables = [self.all_variables[var_id]
                              for var_id in entity_variable_ids
                              if var_id in self.all_variables]
        
        # Always include pending variables for reference
        if pending_variable_ids:
            pending_variables = [self.all_variables[var_id]
                               for var_id in pending_variable_ids
                               if var_id in self.all_variables]
        
        # If view_all is True and we have no variables, show an empty list instead of all variables
        if self.view_all and not entity_variables and not pending_variables:
            print("No variables to display for this entity")
            entity_variables = []
            pending_variables = []

        print(f"Found {len(entity_variables)} entity variables and {len(pending_variables)} pending variables")

        # Ensure all variables have the required methods
        for var in entity_variables + pending_variables:
            if not hasattr(var, 'get_id'):
                var.get_id = lambda v=var: str(id(v))
            if not hasattr(var, 'get_img_path'):
                var.get_img_path = lambda v=var: ""

        self.variables_model.load_data(entity_variables, pending_variables)

    def update_equations_model(self):
        print("\n=== DEBUG: update_equations_model ===")
        print(f"All equations count: {len(self.all_equations)}")

        # Get equation IDs from the entity
        entity_equation_ids = self.editing_entity.get_equations()
        print(f"Entity has {len(entity_equation_ids)} equation IDs: {entity_equation_ids}")

        # Print first few equations for debugging
        print("Sample of all_equations keys:", list(self.all_equations.keys())[:5])

        # If no equations are found, try to get them from the entity's variables
        if not entity_equation_ids and hasattr(self.editing_entity, 'get_variables'):
            var_ids = self.editing_entity.get_variables()
            print(f"No equations found in entity, checking {len(var_ids)} variables for equations...")

            # Try to get equations from variables
            for var_id in var_ids:
                if hasattr(self.editing_entity, 'get_equations_for_var'):
                    eq_ids = self.editing_entity.get_equations_for_var(var_id)
                    if eq_ids:
                        entity_equation_ids.extend(eq_ids)
                        print(f"Found {len(eq_ids)} equations for variable {var_id}")

        # Convert equation IDs to actual equation objects, skipping any that don't exist
        entity_equations = []
        for eq_id in entity_equation_ids:
            if eq_id in self.all_equations:
                entity_equations.append(self.all_equations[eq_id])
            else:
                print(f"Warning: Equation ID '{eq_id}' not found in all_equations")

        print(f"Successfully loaded {len(entity_equations)}/{len(entity_equation_ids)} equations")

        if not entity_equations:
            print("No valid equations found to display!")
            self.equations_model.load_data([])
            return

        # Print debug info for the first few equations
        for i, eq in enumerate(entity_equations[:3]):
            print(f"Equation {i + 1}:")
            print(f"  ID: {getattr(eq, 'id', 'N/A')}")
            print(f"  Type: {type(eq).__name__}")
            print(f"  Has get_id: {hasattr(eq, 'get_id')}")
            print(f"  Has get_img_path: {hasattr(eq, 'get_img_path')}")
            if hasattr(eq, 'lhs'):
                print(f"  LHS: {getattr(eq.lhs, 'to_latex', lambda: str(eq.lhs))()}")
            if hasattr(eq, 'rhs'):
                print(f"  RHS: {getattr(eq.rhs, 'to_latex', lambda: str(eq.rhs))()}")

        # Ensure all equations have the required methods
        for eq in entity_equations:
            if not hasattr(eq, 'get_id'):
                print(f"Adding get_id to equation {eq}")
                eq.get_id = lambda e=eq: getattr(e, 'id', str(id(e)))
            if not hasattr(eq, 'get_img_path'):
                print(f"Adding get_img_path to equation {eq}")
                eq.get_img_path = lambda e=eq: ""

        print(f"Loading {len(entity_equations)} equations into the model")
        self.equations_model.load_data(entity_equations)
        print(f"Model now has {self.equations_model.rowCount()} rows")

    def get_variable_editor_model(self, index):
        var_id = index.data()
        return VariableEditorModel(
                self.editing_entity,
                self.all_variables[var_id],
                self.all_variables,
                self.all_equations,
                )

    def check_variable(self, index):
        var_id = index.data()
        is_top_level = self.editing_entity.is_var_top_level(var_id)
        self.variableChecked.emit(is_top_level)

    def changes_from_delete_var(self, index):
        var_id = index.data()

        self.editing_entity.set_output_var(var_id, False)

        changes = self.editing_entity.generate_var_eq_forest({})
        # TODO: Remove when the entity contain instances instead of str
        changes[0] = [self.all_variables[var_id] for var_id in changes[0]]
        changes[2] = [self.all_variables[var_id] for var_id in changes[2]]
        changes[1] = [self.all_equations[eq_id] for eq_id in changes[1]]
        changes[3] = [self.all_equations[eq_id] for eq_id in changes[3]]

        self.editing_entity.set_output_var(var_id, True)

        return changes

    def accept_changes(self, index):
        var_id = index.data()

        self.editing_entity.set_output_var(var_id, False)
        self.editing_entity.set_init_var(var_id, False)

        self.editing_entity.update_var_eq_tree()

        self.update_variables_model()
        self.update_equations_model()

    def get_unused_variables(self):
        print("\n=== DEBUG: get_unused_variables ===")
        print(f"All variables count: {len(self.all_variables)}")

        # Get the entity type from the entity object if available, otherwise try to parse from name
        ent_type = ""
        if hasattr(self.editing_entity, 'entity_type'):
            ent_type = self.editing_entity.entity_type
            print(f"Using entity_type: {ent_type}")
        elif hasattr(self.editing_entity, 'entity_name'):
            # Fallback to the old method if entity_type is not available
            try:
                ent_type = self.editing_entity.entity_name.split(".")[1]
                print(f"Parsed entity type from name: {ent_type}")
            except (IndexError, AttributeError) as e:
                print(f"Could not parse entity type: {e}")

        print("\n=== DEBUG: get_unused_variables ===")
        print(f"Total variables in all_variables: {len(self.all_variables)}")

        # Get all variable IDs already in the entity
        entity_var_ids = set(self.editing_entity.get_variables())
        print(f"Entity already has {len(entity_var_ids)} variables")

        # Get all available variables that aren't already in the entity
        unused_vars = [
                var for var_id, var in self.all_variables.items()
                if var_id not in entity_var_ids
                ]

        print(f"Found {len(unused_vars)} unused variables")
        return unused_vars

    def add_new_output_var(self, var_id):
        print(f"\n=== DEBUG: add_new_output_var ===")
        print(f"Adding variable {var_id} as output")

        # Set the variable as an output
        self.editing_entity.set_output_var(var_id, True)

        # Generate the variable-equation forest with the new variable
        print("Generating variable-equation forest...")
        self.editing_entity.generate_var_eq_forest({var_id: []})

        # Update the variable-equation tree
        print("Updating variable-equation tree...")
        self.editing_entity.update_var_eq_tree()

        # Print debug info about the entity's state
        print(f"Entity variables after update: {self.editing_entity.get_variables()}")
        print(f"Entity equations after update: {self.editing_entity.get_equations()}")

        # Update the models
        print("Updating models...")
        self.update_variables_model()
        self.update_equations_model()

        # Find and return the index of the new variable
        items = self.variables_model.findItems(var_id)
        if not items:
            print(f"Warning: Could not find variable {var_id} in the model")
            return QtCore.QModelIndex()

        item = items[0]
        index = self.variables_model.indexFromItem(item)
        print(f"Returning index for variable {var_id}: {index}")
        return index
