gui_automaton = {
        "create_node":
            {
                    "accept"            : False,
                    "add_state_variable": True,
                    "add_transport"     : False,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : False,
                    "edit_variable"     : False,
                    "add_intensity"     : False,  # Hidden by default, shown for reservoir entities
                    },
        "create_arc":
            {
                    "accept"            : False,
                    "add_state_variable": False,
                    "add_transport"     : True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : False,
                    "edit_variable"     : False,
                    "add_intensity"     : False,  # Hidden for arcs
                    },
        "create_reservoir":
            {
                    "accept"            : True,   # Show accept button once entity has variables
                    "add_state_variable": False,
                    "add_transport"     : False,
                    "add_variable"      : False,
                    "cancel"            : True,
                    "delete_variable"   : False,  # Disabled until variable selected
                    "edit_variable"     : False,
                    "add_intensity"     : True,   # Keep infinity button visible for adding more secondary states
                    },
        "edit_reservoir":
            {
                    "accept"            : True,
                    "add_state_variable": False,
                    "add_transport"     : False,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : False,  # Disabled until variable selected
                    "edit_variable"     : False,
                    "add_intensity"     : True,   # Keep infinity button visible for adding more secondary states
                    },
        "edit_no_selection_node":
            {
                    "accept"            : True,
                    "add_state_variable": True,
                    "add_transport"     : False,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : False,  # Disabled until variable selected
                    "edit_variable"     : False,
                    "add_intensity"     : False,  # Hidden in edit mode
                    },
        "edit_no_selection_arc":
            {
                    "accept"            : True,
                    "add_state_variable": False,
                    "add_transport"     : True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : False,  # Disabled until variable selected
                    "edit_variable"     : False,
                    "add_intensity"     : False,  # Hidden in edit mode
                    },
        "edit_with_selection_node":
            {
                    "accept"            : True,
                    "add_state_variable": True,
                    "add_transport"     : False,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : True,   # Enabled when variable selected
                    "edit_variable"     : False,
                    "add_intensity"     : True,  # Hidden in edit mode
                    },
        "edit_with_selection_reservoir":
            {
                    "accept"            : True,
                    "add_state_variable": False,  # Reservoirs use intensity button, not state variables
                    "add_transport"     : False,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : True,   # Enabled when variable selected
                    "edit_variable"     : False,
                    "add_intensity"     : True,   # Keep intensity button visible for reservoirs
                    },
        "edit_with_selection_arc":
            {
                    "accept"            : True,
                    "add_state_variable": False,
                    "add_transport"     : True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : True,   # Enabled when variable selected
                    "edit_variable"     : False,
                    "add_intensity"     : True,  # Hidden in edit mode
                    },
        "create":
            {
                    "accept"            : False,
                    "add_state_variable": True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : False,
                    "edit_variable"     : False,
                    "add_intensity"     : False,  # Hidden by default
                    },
        "edit_no_selection":
            {
                    "accept"            : True,
                    "add_state_variable": True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : False,  # Disabled until variable selected
                    "edit_variable"     : False,
                    "add_intensity"     : False,  # Hidden in edit mode
                    },
        "edit_with_selection":
            {
                    "accept"            : True,
                    "add_state_variable": True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : True,   # Enabled when variable selected
                    "edit_variable"     : False,
                    "add_intensity"     : False,  # Hidden in edit mode
                    },
        "edit"  : {
                "accept"            : True,
                "add_state_variable": True,
                "add_variable"      : True,
                "cancel"            : True,
                "delete_variable"   : True,
                "edit_variable"     : False,
                "add_intensity"     : False,  # Hidden in edit mode
                },
        }
