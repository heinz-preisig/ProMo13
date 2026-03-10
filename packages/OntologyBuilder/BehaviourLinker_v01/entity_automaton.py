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
                    },
        "create":
            {
                    "accept"            : False,
                    "add_state_variable": True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : False,
                    "edit_variable"     : False,
                    },
        "edit_no_selection":
            {
                    "accept"            : True,
                    "add_state_variable": True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : False,  # Disabled until variable selected
                    "edit_variable"     : False,
                    },
        "edit_with_selection":
            {
                    "accept"            : True,
                    "add_state_variable": True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_variable"   : True,   # Enabled when variable selected
                    "edit_variable"     : False,
                    },
        "edit"  : {
                "accept"            : True,
                "add_state_variable": True,
                "add_variable"      : True,
                "cancel"            : True,
                "delete_variable"   : True,
                "edit_variable"     : False,
                },
        }
